import random

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Gallery, GalleryPhoto, GallerySelection, Photo, PhotoEssay


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
        return PhotoEssay.objects.filter(is_published=True).prefetch_related('photos', 'photo_links')


class PhotoEssayDetailView(DetailView):
    """Display a single photo essay with all its photos."""
    model = PhotoEssay
    template_name = 'photography/essay_detail.html'
    context_object_name = 'essay'
    slug_field = 'slug'

    def get_queryset(self):
        return PhotoEssay.objects.filter(is_published=True).prefetch_related('photos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        essay = context.get('essay')
        links = list(essay.photo_links.select_related('photo')) if essay else []

        ordered_links = [link for link in links if link.display_order > 0]
        unordered_links = [link for link in links if link.display_order == 0]

        ordered_links.sort(key=lambda link: link.display_order)

        if essay and essay.layout == 'masonry':
            random.shuffle(unordered_links)
        else:
            unordered_links.sort(key=lambda link: link.photo.created_at, reverse=True)

        context['photos_for_display'] = [link.photo for link in ordered_links + unordered_links]
        return context


class PhotoListView(ListView):
    """Display all photos not part of an essay."""
    model = Photo
    template_name = 'photography/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 20

    def get_queryset(self):
        return Photo.objects.filter(essays__isnull=True).distinct()


class PhotoDetailView(DetailView):
    """Display a single photo."""
    model = Photo
    template_name = 'photography/photo_detail.html'
    context_object_name = 'photo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = context.get('photo')
        if photo:
            context['primary_essay'] = photo.essays.order_by('-created_at').first()
        else:
            context['primary_essay'] = None
        return context


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _gallery_access_key(request, gallery):
    key = request.GET.get("key")
    if key and str(gallery.access_key) == key:
        request.session[f"gallery_access_{gallery.id}"] = True
        return True
    return False


def _has_gallery_access(request, gallery):
    if gallery.is_public:
        return True
    if request.session.get(f"gallery_access_{gallery.id}"):
        return True
    return _gallery_access_key(request, gallery)


class GalleryListView(ListView):
    """Display public galleries."""
    model = Gallery
    template_name = "photography/gallery_list.html"
    context_object_name = "galleries"
    paginate_by = 12

    def get_queryset(self):
        return Gallery.objects.filter(is_public=True).prefetch_related("photos")


class GalleryDetailView(DetailView):
    """Display a single gallery with its photos."""
    model = Gallery
    template_name = "photography/gallery_detail.html"
    context_object_name = "gallery"
    slug_field = "slug"

    def dispatch(self, request, *args, **kwargs):
        gallery = self.get_object()
        if not _has_gallery_access(request, gallery):
            return redirect("photography:gallery_access", slug=gallery.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Gallery.objects.prefetch_related("photos", "photo_links")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gallery = context.get("gallery")
        links = list(gallery.photo_links.select_related("photo")) if gallery else []

        ordered_links = [link for link in links if link.display_order > 0]
        unordered_links = [link for link in links if link.display_order == 0]

        ordered_links.sort(key=lambda link: link.display_order)
        unordered_links.sort(key=lambda link: link.photo.created_at, reverse=True)

        context["photos_for_display"] = [link.photo for link in ordered_links + unordered_links]

        session_key = _ensure_session_key(self.request)
        selections = GallerySelection.objects.filter(
            gallery=gallery,
            session_key=session_key,
        ).values_list("photo_id", flat=True)
        context["favorite_photo_ids"] = set(selections)
        context["download_url"] = gallery.download_url
        return context


class GalleryAccessView(TemplateView):
    """Prompt for gallery access when protected."""
    template_name = "photography/gallery_access.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gallery = get_object_or_404(Gallery, slug=self.kwargs.get("slug"))
        context["gallery"] = gallery
        return context

    def post(self, request, *args, **kwargs):
        gallery = get_object_or_404(Gallery, slug=self.kwargs.get("slug"))
        password = request.POST.get("password", "")
        if gallery.check_password(password):
            request.session[f"gallery_access_{gallery.id}"] = True
            return redirect("photography:gallery_detail", slug=gallery.slug)
        context = self.get_context_data(**kwargs)
        context["error"] = "Incorrect password."
        return self.render_to_response(context)


@method_decorator(require_POST, name="dispatch")
class GalleryToggleFavoriteView(View):
    """Toggle a photo as favorite for proofing."""

    def post(self, request, *args, **kwargs):
        gallery = get_object_or_404(Gallery, slug=kwargs.get("slug"))
        photo = get_object_or_404(Photo, pk=kwargs.get("pk"))

        if not _has_gallery_access(request, gallery):
            return JsonResponse({"error": "unauthorized"}, status=403)

        session_key = _ensure_session_key(request)
        selection, created = GallerySelection.objects.get_or_create(
            gallery=gallery,
            photo=photo,
            session_key=session_key,
        )

        if not created:
            selection.delete()

        total = GallerySelection.objects.filter(
            gallery=gallery,
            session_key=session_key,
        ).count()

        return JsonResponse({"selected": created, "total": total})
