from django.contrib import admin
from .models import Track, Race

# Register your models here.
class RaceAdmin(admin.ModelAdmin):
    """
    """


class TrackAdmin(admin.ModelAdmin):
    """
    """

admin.site.register(Race, RaceAdmin)
admin.site.register(Track, TrackAdmin)