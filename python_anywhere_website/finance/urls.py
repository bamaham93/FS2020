from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("by-month", views.transactions_by_month, name="transactions_by_month"),
    path("by_month/<int:month>/<int:year>", views.transactions_by_month, name="transactions_by_month"),
]
