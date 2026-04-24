from django.contrib import admin
from prayer.models import (
    PrayerGroup,
    PrayerProfile,
    Person,
    PrayerMessage,
    SMSLog,
    InboundSmsMessage,
)


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
        "phone_number",
        "email",
        "sms_consent",
        "is_admin",
    )
    fields = (
        ("first_name", "last_name"),
        ("phone_number", "email"),
        ("sms_consent", "sms_consent_date"),
        ("is_admin",),
    )
    empty_value = "-empty-"


@admin.register(PrayerMessage)
class PrayerMessageAdmin(admin.ModelAdmin):
    """ """

    list_display = ("name", "subject", "created_at")
    filter_horizontal = ("groups",)


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
