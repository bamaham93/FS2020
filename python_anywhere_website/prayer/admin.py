from difflib import SequenceMatcher

from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from prayer.models import (
    PrayerGroup,
    PrayerProfile,
    Person,
    PrayerMessage,
    SMSLog,
    InboundSmsMessage,
)


def _normalized(value):
    return " ".join(str(value or "").lower().split())


def _name_for_user(user):
    full_name = user.get_full_name().strip()
    return full_name or user.username


def _similarity(left, right):
    left_normalized = _normalized(left)
    right_normalized = _normalized(right)
    if not left_normalized or not right_normalized:
        return 0
    return round(SequenceMatcher(None, left_normalized, right_normalized).ratio() * 100)


def suggest_user_for_person(person):
    if not person:
        return None, 0, "Save this person before suggestions are available."

    if person.user_id:
        return person.user, 100, "Already linked."

    if person.email:
        email_match = User.objects.filter(email__iexact=person.email).first()
        if email_match:
            return email_match, 100, "Exact email match."

    person_name = f"{person.first_name} {person.last_name}".strip()
    best_user = None
    best_score = 0

    for user in User.objects.all():
        score = max(
            _similarity(person_name, user.get_full_name()),
            _similarity(person_name, user.username),
        )
        if person.first_name:
            score = max(score, _similarity(person.first_name, user.first_name))
        if person.last_name:
            score = max(score, _similarity(person.last_name, user.last_name))

        if score > best_score:
            best_user = user
            best_score = score

    if best_user and best_score >= 70:
        return best_user, best_score, "Similar name or username."

    return None, best_score, "No confident match found."


# Register your models here.
@admin.register(PrayerGroup)
class GroupAdmin(admin.ModelAdmin):
    """ """


@admin.register(PrayerProfile)
class PrayerProfileAdmin(admin.ModelAdmin):
    """ """


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """ """

    list_display = (
        "first_name",
        "last_name",
        "user",
        "phone_number",
        "email",
        "sms_consent",
        "suggested_user",
    )
    list_select_related = ("user",)
    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    autocomplete_fields = ("user",)
    readonly_fields = ("suggested_user_match",)
    fields = (
        "user",
        "suggested_user_match",
        ("first_name", "last_name"),
        ("phone_number", "email"),
        ("sms_consent", "sms_consent_date"),
    )
    empty_value = "-empty-"

    @admin.display(description="Suggested user")
    def suggested_user(self, obj):
        user, score, _reason = suggest_user_for_person(obj)
        if not user:
            return "No confident match"
        return f"{_name_for_user(user)} ({score}%)"

    @admin.display(description="Suggested user match")
    def suggested_user_match(self, obj):
        user, score, reason = suggest_user_for_person(obj)
        if not user:
            return f"{reason} Best score: {score}%."

        url = reverse("admin:auth_user_change", args=[user.pk])
        return format_html(
            '<a href="{}">{}</a> - {}% confidence. {}',
            url,
            _name_for_user(user),
            score,
            reason,
        )


@admin.register(PrayerMessage)
class PrayerMessageAdmin(admin.ModelAdmin):
    """ """

    list_display = ("name", "subject", "created_at")
    filter_horizontal = ("groups", "direct_recipients")


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    """Read-only log of every SMS send attempt."""

    list_display = ("message", "recipient", "sent_at", "success", "sent_by")
    list_filter = ("success",)
    readonly_fields = (
        "message",
        "recipient",
        "sent_at",
        "success",
        "error_message",
        "sent_by",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(InboundSmsMessage)
class InboundSmsMessageAdmin(admin.ModelAdmin):
    list_display = (
        "provider_message_id",
        "from_number",
        "to_number",
        "person",
        "received_at",
        "processed",
    )
    list_filter = ("processed", "provider", "received_at")
    search_fields = ("provider_message_id", "from_number", "to_number", "body")
    readonly_fields = (
        "provider",
        "provider_message_id",
        "from_number",
        "to_number",
        "body",
        "received_at",
        "direction",
    )
