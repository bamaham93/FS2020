from django.contrib import admin
from .models import Aircraft, Flight

class AircraftAdmin(admin.ModelAdmin):
    list_display = ("n_num", "icao_location", "make", "model")


class FlightAdmin(admin.ModelAdmin):
    pass

# Register your models here.
admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Flight, FlightAdmin)