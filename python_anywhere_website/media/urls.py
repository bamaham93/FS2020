from django.urls import path
from . import views

app_name = "media"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("movies", views.movies, name="movies"),
    path("books", views.books, name="books"),
    path('cds', views.cds, name='cds'),
    path('dvds', views.dvds, name='dvds'),
    path('amazon', views.amazon, name='amazon'),
    path('youtube', views.youtube, name='youtube'),
    path('digital-dl', views.digital_dl, name="digital_dl"),
    path('vhs', views.vhs, name='vhs'),
]
