from django import template
from django.conf import settings

register = template.Library()


@register.filter
def media_image_url(obj):
    """Return a usable image URL for a media object or a sensible fallback."""
    try:
        if obj and getattr(obj, "image"):
            return obj.image.url
    except Exception:
        pass

    try:
        url = getattr(obj, "image_url", None) or getattr(obj, "thumbnail", None)
        if url:
            return url
    except Exception:
        pass

    return "https://images.unsplash.com/photo-1528928441742-b4ccac1bb04c?auto=format&fit=crop&w=800&q=60"
