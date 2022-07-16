from django.contrib import admin
from .models import Track, Race, Driver, League

# Register your models here.
@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    """

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """
    """


# admin.site.register(Race, RaceAdmin)
# admin.site.register(Track, TrackAdmin)
# admin.site.register(Driver, DriverAdmin)
# admin.site.register(League, LeagueAdmin)