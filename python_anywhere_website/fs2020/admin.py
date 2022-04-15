from django.contrib import admin
from .models import Aircraft

class AircraftAdmin(admin.ModelAdmin):
    list_display = ("n_num", "icao_location", "make", "model")

# Register your models here.
admin.site.register(Aircraft, AircraftAdmin)