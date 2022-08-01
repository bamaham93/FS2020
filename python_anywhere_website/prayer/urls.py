from django.urls import path

from . import views

app_name = "prayer"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('new-message', views.new_message, name='new_message'),
    path('groups', views.groups, name='groups'),
    path('prayer-requests', views.prayer_requests, name='prayer_requests'),
]