from django.urls import path

from . import views

app_name = "prayer"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('new-message', views.new_message, name='new_message'),
    path('groups', views.groups, name='groups'),
    path('prayer-requests', views.prayer_requests, name='prayer_requests'),
    path('people', views.people, name='people'),
    path('delete-person/<person_id>', views.delete_person, name='delete_person'),
]
