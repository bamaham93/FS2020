from django.contrib import admin
from .models import Photo, PhotoEssay


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('title', 'image', 'external_url', 'display_order', 'image_alt_text')
    help_texts = {
        'image': 'Upload a local image OR provide an external URL below (only one needed)',
        'external_url': 'Link to photos hosted elsewhere (Flickr, Google Photos, etc.)',
    }

    def save_model(self, request, obj, form, change):
        """Call clean() before saving to validate at least one image source."""
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(PhotoEssay)
class PhotoEssayAdmin(admin.ModelAdmin):
    list_display = ('title', 'layout', 'is_published', 'created_at', 'photo_count')
    list_filter = ('is_published', 'layout', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PhotoInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'is_published')
        }),
        ('Display Settings', {
            'fields': ('layout', 'cover_image'),
            'description': 'Choose a layout style and optionally add a cover image'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def photo_count(self, obj):
        """Display the number of photos in the essay."""
        return obj.photos.count()
    photo_count.short_description = 'Photos'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'essay', 'display_order', 'has_image', 'created_at')
    list_filter = ('essay', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('essay', 'display_order')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'essay', 'display_order')
        }),
        ('Image (Choose One)', {
            'fields': ('image', 'external_url'),
            'description': 'Either upload a local image or provide an external URL. Leave one blank if using the other.'
        }),
        ('Accessibility', {
            'fields': ('image_alt_text',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """Call full_clean() before saving to validate photo."""
        obj.full_clean()
        super().save_model(request, obj, form, change)
