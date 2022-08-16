from django.contrib import admin
from .models import Media, MediaFormat, MediaType, MediaGenre, MediaLocation

# Register your models here.
@admin.register(Media)
class AdminMedia(admin.ModelAdmin):
    """
    """


@admin.register(MediaFormat)
class AdminMediaFormat(admin.ModelAdmin):
    """
    """


@admin.register(MediaType)
class AdminMediaType(admin.ModelAdmin):
    """
    """


@admin.register(MediaGenre)
class AdminMediaGenre(admin.ModelAdmin):
    """
    """


@admin.register(MediaLocation)
class AdminMediaLocation(admin.ModelAdmin):
    """
    """