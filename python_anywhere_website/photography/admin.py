from django import forms
from django.contrib import admin

from .models import (
    Gallery,
    GalleryPhoto,
    GallerySelection,
    Photo,
    PhotoEssay,
    PhotoEssayPhoto,
)


class PhotoEssayPhotoInline(admin.TabularInline):
    model = PhotoEssayPhoto
    extra = 1
    fields = ("photo", "display_order")
    autocomplete_fields = ("photo",)


class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 1
    fields = ("photo", "display_order")
    autocomplete_fields = ("photo",)


class GalleryAdminForm(forms.ModelForm):
    raw_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Set or change the gallery password. Leave blank to keep current.",
    )
    clear_password = forms.BooleanField(
        required=False,
        help_text="Clear the current password.",
    )

    class Meta:
        model = Gallery
        exclude = ("password",)

    def save(self, commit=True):
        gallery = super().save(commit=False)
        raw_password = self.cleaned_data.get("raw_password")
        clear_password = self.cleaned_data.get("clear_password")

        if clear_password:
            gallery.set_password("")
        elif raw_password:
            gallery.set_password(raw_password)

        if commit:
            gallery.save()
            self.save_m2m()
        return gallery


@admin.register(PhotoEssay)
class PhotoEssayAdmin(admin.ModelAdmin):
    list_display = ('title', 'layout', 'is_featured', 'is_published', 'created_at', 'photo_count')
    list_filter = ('is_published', 'is_featured', 'layout', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PhotoEssayPhotoInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'is_published')
        }),
        ('Display Settings', {
            'fields': (
                'layout',
                'cover_image',
                'is_featured',
                'show_essay_title',
                'show_photo_titles',
            ),
            'description': 'Choose a layout style, optional cover image, and what to display for this essay'
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
    list_display = ('title', 'has_image', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
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


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    form = GalleryAdminForm
    list_display = ("title", "is_public", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GalleryPhotoInline]
    readonly_fields = ("created_at", "updated_at", "access_key")
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("title", "slug", "description", "cover_image"),
            },
        ),
        (
            "Access",
            {
                "fields": (
                    "is_public",
                    "raw_password",
                    "clear_password",
                    "access_key",
                    "download_url",
                ),
                "description": "Use a password for private galleries or share the access key.",
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(GallerySelection)
class GallerySelectionAdmin(admin.ModelAdmin):
    list_display = ("gallery", "photo", "session_key", "created_at")
    list_filter = ("gallery", "created_at")
    search_fields = ("gallery__title", "photo__title", "session_key")
