from django.urls import path

from . import views

app_name = "fs2020"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
]