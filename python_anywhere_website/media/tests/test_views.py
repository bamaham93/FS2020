from django.test import TestCase, Client

# Create your tests here.
class TestMediaViews(TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.c = Client(enforce_csrf_checks=True)

    def test_media_index(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/index.html")

    def test_movies(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/movies')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/movies.html")

    def test_add_media(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/add_media')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/add_media.html")

    def test_books(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/books')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/books.html")

    def test_cds(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/cds')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/cds.html")

    def test_dvds(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/dvds')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/dvds.html")

    def test_amazon(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/amazon')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/amazon.html")

    def test_youtube(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/youtube')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/youtube.html")

    def test_digital(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/digital-dl')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/digital_dl.html")

    def test_vhs(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/vhs')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/vhs.html")

    def test_sorted_by(self):
        """
        """
        # Check page returns OK.
        response = self.c.get('/media/sorted_by')
        self.assertEqual(response.status_code, 200)

        # Test Templates used
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/sorted_by.html")
