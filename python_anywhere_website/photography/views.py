from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from .models import Photo, PhotoEssay


class DebugPhotographyView(TemplateView):
    """Debug view to show database contents."""
    template_name = 'photography/debug.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_essays'] = PhotoEssay.objects.filter(
            is_published=True,
            is_featured=True
        ).prefetch_related('photos')
        return context


class PhotographyDashboardView(TemplateView):
    """Display featured photography essays on the dashboard."""
    template_name = 'photography/dashboard.html'
    context_object_name = 'featured_essays'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_essays'] = PhotoEssay.objects.filter(
            is_published=True,
            is_featured=True
        ).prefetch_related('photos')
        context['all_essays_count'] = PhotoEssay.objects.filter(is_published=True).count()
        return context


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
