import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class PhotoEssay(models.Model):
    """A collection of photos with a theme or narrative."""
    
    LAYOUT_CHOICES = [
        ('sequential_large', 'Sequential - Large Photos (1 per row)'),
        ('sequential_medium', 'Sequential - Medium Photos (2 per row)'),
        ('sequential_small', 'Sequential - Small Photos (3 per row)'),
        ('masonry', 'Masonry Grid'),
        ('collage_mixed', 'Collage - Mixed Sizes'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='photo_essays/', null=True, blank=True)
    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='sequential_medium',
        help_text="Choose how photos are displayed in this essay"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured essays appear on the photography dashboard"
    )
    show_essay_title = models.BooleanField(
        default=True,
        help_text="Show the essay title header on the detail page"
    )
    show_photo_titles = models.BooleanField(
        default=True,
        help_text="Show photo titles and captions inside the essay"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    photos = models.ManyToManyField(
        "Photo",
        through="PhotoEssayPhoto",
        related_name="essays",
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Photo Essays"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Photo(models.Model):
    """A single photograph."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='photos/', 
        null=True, 
        blank=True,
        help_text="Upload a local image (or provide an external URL below)"
    )
    external_url = models.URLField(
        blank=True,
        help_text="Link to a photo hosted elsewhere (e.g., Flickr, Google Photos). Leave blank if uploading locally."
    )
    image_alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for accessibility")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_image_url(self):
        """Return the image URL, preferring external_url if available."""
        if self.external_url:
            return self.external_url
        elif self.image:
            return self.image.url
        return None

    def has_image(self):
        """Check if photo has either a local image or external URL."""
        return bool(self.image or self.external_url)

    def clean(self):
        """Validate that at least one image source is provided."""
        if not self.image and not self.external_url:
            raise ValidationError(
                'Please provide either a local image or an external URL.'
            )


class PhotoEssayPhoto(models.Model):
    """Join table for photos in essays with per-essay ordering."""
    essay = models.ForeignKey(
        PhotoEssay,
        on_delete=models.CASCADE,
        related_name="photo_links",
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="essay_links",
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order to display photos within this essay",
    )

    class Meta:
        ordering = ["display_order", "photo__created_at"]
        unique_together = ("essay", "photo")

    def __str__(self):
        return f"{self.essay} - {self.photo}"


class Gallery(models.Model):
    """Client gallery with optional password protection."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="gallery_covers/", null=True, blank=True)
    is_public = models.BooleanField(
        default=False,
        help_text="Allow public access without a password",
    )
    password = models.CharField(max_length=128, blank=True)
    access_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    download_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photos = models.ManyToManyField(
        "Photo",
        through="GalleryPhoto",
        related_name="galleries",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        if raw_password:
            self.password = make_password(raw_password)
        else:
            self.password = ""

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)


class GalleryPhoto(models.Model):
    """Join table for photos in galleries with per-gallery ordering."""
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name="photo_links",
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="gallery_links",
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order to display photos within this gallery",
    )

    class Meta:
        ordering = ["display_order", "photo__created_at"]
        unique_together = ("gallery", "photo")

    def __str__(self):
        return f"{self.gallery} - {self.photo}"


class GallerySelection(models.Model):
    """Stores per-session favorites for proofing."""
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name="selections",
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="gallery_selections",
    )
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("gallery", "photo", "session_key")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.gallery} - {self.photo}"
