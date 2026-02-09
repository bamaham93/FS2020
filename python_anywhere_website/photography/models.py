from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

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
    essay = models.ForeignKey(
        PhotoEssay, 
        on_delete=models.CASCADE, 
        related_name='photos',
        null=True,
        blank=True
    )
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
    display_order = models.IntegerField(default=0, help_text="Order to display photos within an essay")

    class Meta:
        ordering = ['display_order', '-created_at']

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
