from django.urls import path
from . import views

app_name = 'photography'

urlpatterns = [
    path('', views.PhotoEssayListView.as_view(), name='essay_list'),
    path('photos/', views.PhotoListView.as_view(), name='photo_list'),
    path('essay/<slug:slug>/', views.PhotoEssayDetailView.as_view(), name='essay_detail'),
]
