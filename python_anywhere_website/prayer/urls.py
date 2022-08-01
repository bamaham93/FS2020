from django.urls import path

from . import views

app_name = "prayer"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
]