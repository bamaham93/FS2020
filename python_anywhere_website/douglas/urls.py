from django.urls import path

from . import views

app_name = "douglas"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.nis_index, name='index'),
    path('nis/index', views.nis_index, name='nis_index'),
    path('add-race-results', views.add_race_result, name='add_race_results'),
]