from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import PhotoEssay, Photo


class PhotoEssayTestCase(TestCase):
    """Test cases for PhotoEssay model."""

    def setUp(self):
        """Create test data."""
        self.essay = PhotoEssay.objects.create(
            title="Test Essay",
            description="A test photo essay",
            is_published=True
        )

    def test_essay_creation(self):
        """Test that a photo essay can be created."""
        self.assertEqual(self.essay.title, "Test Essay")
        self.assertTrue(self.essay.is_published)

    def test_essay_slug_creation(self):
        """Test that slug is automatically created from title."""
        self.assertEqual(self.essay.slug, "test-essay")

    def test_essay_ordering(self):
        """Test that essays are ordered by creation date (newest first)."""
        new_essay = PhotoEssay.objects.create(title="New Essay")
        essays = PhotoEssay.objects.all()
        self.assertEqual(essays[0], new_essay)


class PhotoTestCase(TestCase):
    """Test cases for Photo model."""

    def setUp(self):
        """Create test data."""
        self.essay = PhotoEssay.objects.create(
            title="Test Essay",
            is_published=True
        )

    def test_photo_with_local_image_url(self):
        """Test that photo can use local image URL."""
        photo = Photo.objects.create(
            title="Local Photo",
            essay=self.essay,
            image="test_image.jpg"
        )
        self.assertEqual(photo.get_image_url(), photo.image.url)
        self.assertTrue(photo.has_image())

    def test_photo_with_external_url(self):
        """Test that photo can use external URL."""
        external_url = "https://example.com/photo.jpg"
        photo = Photo.objects.create(
            title="External Photo",
            essay=self.essay,
            external_url=external_url
        )
        self.assertEqual(photo.get_image_url(), external_url)
        self.assertTrue(photo.has_image())

    def test_external_url_preferred_over_local(self):
        """Test that external_url is preferred when both are provided."""
        external_url = "https://example.com/photo.jpg"
        photo = Photo.objects.create(
            title="Both Photos",
            essay=self.essay,
            image="test_image.jpg",
            external_url=external_url
        )
        self.assertEqual(photo.get_image_url(), external_url)

    def test_photo_without_image_fails_validation(self):
        """Test that photo without image or external_url fails validation."""
        photo = Photo(
            title="No Image Photo",
            essay=self.essay
        )
        with self.assertRaises(ValidationError):
            photo.full_clean()

    def test_photo_with_alt_text(self):
        """Test that alt text can be set for accessibility."""
        photo = Photo.objects.create(
            title="Accessible Photo",
            essay=self.essay,
            external_url="https://example.com/photo.jpg",
            image_alt_text="A descriptive alt text"
        )
        self.assertEqual(photo.image_alt_text, "A descriptive alt text")

    def test_photo_display_order(self):
        """Test that photos are ordered by display_order."""
        photo1 = Photo.objects.create(
            title="First Photo",
            essay=self.essay,
            external_url="https://example.com/1.jpg",
            display_order=1
        )
        photo2 = Photo.objects.create(
            title="Second Photo",
            essay=self.essay,
            external_url="https://example.com/2.jpg",
            display_order=2
        )
        photos = Photo.objects.filter(essay=self.essay)
        self.assertEqual(photos[0], photo1)
        self.assertEqual(photos[1], photo2)

    def test_standalone_photo(self):
        """Test that photo can exist without an essay."""
        photo = Photo.objects.create(
            title="Standalone Photo",
            external_url="https://example.com/standalone.jpg"
        )
        self.assertIsNone(photo.essay)
        self.assertTrue(photo.has_image())

