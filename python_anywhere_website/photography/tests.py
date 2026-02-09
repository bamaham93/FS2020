from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
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

    def test_essay_is_featured(self):
        """Test that essays can be marked as featured."""
        self.assertFalse(self.essay.is_featured)
        self.essay.is_featured = True
        self.essay.save()
        self.assertTrue(self.essay.is_featured)

    def test_featured_essays_query(self):
        """Test filtering for featured essays."""
        featured_essay = PhotoEssay.objects.create(
            title="Featured Essay",
            is_published=True,
            is_featured=True
        )
        unfeatured_essay = PhotoEssay.objects.create(
            title="Regular Essay",
            is_published=True,
            is_featured=False
        )
        featured = PhotoEssay.objects.filter(is_featured=True, is_published=True)
        self.assertEqual(featured.count(), 1)
        self.assertEqual(featured[0], featured_essay)


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


class PhotographyViewsTestCase(TestCase):
    """Test cases for photography views."""

    def setUp(self):
        """Create test data."""
        self.client = Client()
        
        # Create featured essays
        self.featured_essay1 = PhotoEssay.objects.create(
            title="Featured Essay 1",
            description="First featured essay",
            is_published=True,
            is_featured=True
        )
        self.featured_essay2 = PhotoEssay.objects.create(
            title="Featured Essay 2",
            description="Second featured essay",
            is_published=True,
            is_featured=True
        )
        
        # Create non-featured essay
        self.regular_essay = PhotoEssay.objects.create(
            title="Regular Essay",
            description="A regular essay",
            is_published=True,
            is_featured=False
        )
        
        # Create unpublished essay
        self.unpublished_essay = PhotoEssay.objects.create(
            title="Unpublished Essay",
            is_published=False,
            is_featured=True
        )

    def test_dashboard_view_displays_featured_essays(self):
        """Test that the dashboard displays only featured published essays."""
        response = self.client.get(reverse('photography:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('featured_essays', response.context)
        featured_essays = response.context['featured_essays']
        self.assertEqual(featured_essays.count(), 2)
        self.assertIn(self.featured_essay1, featured_essays)
        self.assertIn(self.featured_essay2, featured_essays)

    def test_dashboard_does_not_show_regular_essays(self):
        """Test that non-featured essays don't appear on dashboard."""
        response = self.client.get(reverse('photography:dashboard'))
        featured_essays = response.context['featured_essays']
        self.assertNotIn(self.regular_essay, featured_essays)

    def test_dashboard_does_not_show_unpublished_essays(self):
        """Test that unpublished essays don't appear on dashboard."""
        response = self.client.get(reverse('photography:dashboard'))
        featured_essays = response.context['featured_essays']
        self.assertNotIn(self.unpublished_essay, featured_essays)

    def test_essay_list_view_shows_all_published(self):
        """Test that essay list shows all published essays."""
        response = self.client.get(reverse('photography:essay_list'))
        self.assertEqual(response.status_code, 200)
        essays = response.context['essays']
        self.assertEqual(essays.count(), 3)

    def test_essay_detail_view(self):
        """Test viewing a specific essay detail."""
        response = self.client.get(
            reverse('photography:essay_detail', args=[self.featured_essay1.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['essay'], self.featured_essay1)

    def test_photo_list_view(self):
        """Test the standalone photos list view."""
        # Create a standalone photo
        standalone_photo = Photo.objects.create(
            title="Standalone",
            external_url="https://example.com/photo.jpg"
        )
        
        response = self.client.get(reverse('photography:photo_list'))
        self.assertEqual(response.status_code, 200)
        photos = response.context['photos']
        self.assertIn(standalone_photo, photos)


