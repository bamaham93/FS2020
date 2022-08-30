from django.urls import path

from . import views

app_name = "fs2020"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("flights", views.flights, name="flights"),
    path("flights/<str:n_number>", views.flights, name="flights"),
    path("notams", views.notams, name="notams"),
]
