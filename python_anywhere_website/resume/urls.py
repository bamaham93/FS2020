from django.urls import path

from . import views

app_name = "resume"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('aviation', views.aviation, name="aviation"),
    path('tech', views.tech, name='tech'),
]