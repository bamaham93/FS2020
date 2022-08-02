from django.contrib import admin
from prayer.models import PrayerGroup, PrayerProfile, Person

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
