from django.urls import path

from . import views

app_name = "fs2020"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("flights", views.flights, name="flights"),
    path("flights/<str:n_number>", views.flights, name="flights"),
    path("notams", views.notams, name="notams"),
    path("aircraft/add/", views.aircraft_add, name="aircraft_add"),
    path("aircraft/<int:pk>/edit/", views.aircraft_edit, name="aircraft_edit"),
    path("api/metar/", views.metar_api, name="metar_api"),
    path("o2-calculator/", views.o2_calculator, name="o2_calculator"),
]
