from django.urls import path
from . import views

app_name = 'photography'

urlpatterns = [
    path('', views.PhotographyDashboardView.as_view(), name='dashboard'),
    path('essays/', views.PhotoEssayListView.as_view(), name='essay_list'),
    path('photos/', views.PhotoListView.as_view(), name='photo_list'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('essay/<slug:slug>/', views.PhotoEssayDetailView.as_view(), name='essay_detail'),
    path('debug/', views.DebugPhotographyView.as_view(), name='debug'),
]
