from django.urls import path
from . import views

app_name = 'photography'

urlpatterns = [
    path('', views.PhotographyDashboardView.as_view(), name='dashboard'),
    path('essays/', views.PhotoEssayListView.as_view(), name='essay_list'),
    path('photos/', views.PhotoListView.as_view(), name='photo_list'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('galleries/', views.GalleryListView.as_view(), name='gallery_list'),
    path('gallery/<slug:slug>/', views.GalleryDetailView.as_view(), name='gallery_detail'),
    path('gallery/<slug:slug>/access/', views.GalleryAccessView.as_view(), name='gallery_access'),
    path(
        'gallery/<slug:slug>/favorite/<int:pk>/',
        views.GalleryToggleFavoriteView.as_view(),
        name='gallery_toggle_favorite'
    ),
    path('essay/<slug:slug>/', views.PhotoEssayDetailView.as_view(), name='essay_detail'),
    path('debug/', views.DebugPhotographyView.as_view(), name='debug'),
]
