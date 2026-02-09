from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Photo, PhotoEssay


class PhotoEssayListView(ListView):
    """Display all published photo essays."""
    model = PhotoEssay
    template_name = 'photography/essay_list.html'
    context_object_name = 'essays'
    paginate_by = 12

    def get_queryset(self):
        return PhotoEssay.objects.filter(is_published=True).prefetch_related('photos')


class PhotoEssayDetailView(DetailView):
    """Display a single photo essay with all its photos."""
    model = PhotoEssay
    template_name = 'photography/essay_detail.html'
    context_object_name = 'essay'
    slug_field = 'slug'

    def get_queryset(self):
        return PhotoEssay.objects.filter(is_published=True).prefetch_related('photos')


class PhotoListView(ListView):
    """Display all photos not part of an essay."""
    model = Photo
    template_name = 'photography/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 20

    def get_queryset(self):
        return Photo.objects.filter(essay__isnull=True)
