from django import template
from django.conf import settings

register = template.Library()


@register.filter
def media_image_url(obj):
    """Return a usable image URL for a media object or a sensible fallback."""
    # Prefer explicit ImageField on the model
    try:
        if obj and getattr(obj, 'image'):
            return obj.image.url
    except Exception:
        pass

    # Try common alternate attributes
    try:
        url = getattr(obj, 'image_url', None) or getattr(obj, 'thumbnail', None)
        if url:
            return url
    except Exception:
        pass

    # Generic fallback (kept consistent with existing design)
    return 'https://images.unsplash.com/photo-1528928441742-b4ccac1bb04c?auto=format&fit=crop&w=800&q=60'
