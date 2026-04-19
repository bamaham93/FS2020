from django.contrib import admin
from prayer.models import PrayerGroup, PrayerProfile, Person, PrayerMessage, SMSLog


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

    list_display = ("first_name", "last_name", "phone_number", "email")
    fields = (("first_name", "last_name"), ("phone_number", "email"))
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
