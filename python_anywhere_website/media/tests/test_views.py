from django.test import TestCase, Client
from media.forms import AddMediaForm
from django.contrib.auth.models import User


# Create your tests here.
class TestMediaViews(TestCase):
    """
    """

    def setUp(self):
        """
        """
        # To check pages with forms
        self.c = Client()


    def setup_login(self):
        """
        Sets up login only when required. Makes the tests much more performant.
        """
        # To login_required pages; this user not logged in.
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.jim = Client(test_user1)

        # To check login_required_pages; this user logged in.
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.bob = Client()
        self.bob.force_login(test_user2)


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
        Tests with and without login.
        """
        self.setup_login()
        # Check page returns 302 if not logged in.
        response = self.c.get('/media/add_media')
        self.assertEqual(response.status_code, 302)

        # Check login_required
        response1 = self.bob.get('/media/add_media')
        self.assertEqual(response1.status_code, 200)

        self.assertTemplateUsed(response1, 'media/media_base.html')
        self.assertTemplateUsed(response1, 'media/add_media.html')

    def test_add_media_form(self):
        """
        """
        self.setup_login()
        add_media_form = AddMediaForm()
        response = self.bob.post("/media/add_media")

        self.assertEqual(response.status_code, 200)

    def test_add_media_templates(self):
        """
        """
        response = self.c.get("/media/add-media")
        # self.assertTemplateUsed(response, "media/media_base.html")
        # self.assertTemplateUsed(response, "media/add_media.html")

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
