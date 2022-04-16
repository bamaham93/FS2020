from django.contrib import admin
from .models import Track, Race, Driver

# Register your models here.
class RaceAdmin(admin.ModelAdmin):
    """
    """


class TrackAdmin(admin.ModelAdmin):
    """
    """


class DriverAdmin(admin.ModelAdmin):
    """
    """

admin.site.register(Race, RaceAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Driver, DriverAdmin)