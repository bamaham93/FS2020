from django.test import TestCase, Client
from media_app.forms import AddMediaForm
from django.contrib.auth.models import User


class TestMediaViews(TestCase):
    def setUp(self):
        self.c = Client()

    def setup_login(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.jim = Client(test_user1)
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.bob = Client()
        self.bob.force_login(test_user2)

    def test_media_index(self):
        response = self.c.get('/media/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/index.html")

    def test_movies(self):
        response = self.c.get('/media/movies')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/movies.html")

    def test_add_media(self):
        self.setup_login()
        response = self.c.get('/media/add_media')
        self.assertEqual(response.status_code, 302)
        response1 = self.bob.get('/media/add_media')
        self.assertEqual(response1.status_code, 200)
        self.assertTemplateUsed(response1, 'media/media_base.html')
        self.assertTemplateUsed(response1, 'media/add_media.html')

    def test_add_media_form(self):
        self.setup_login()
        add_media_form = AddMediaForm()
        response = self.bob.post("/media/add_media")
        self.assertEqual(response.status_code, 200)

    def test_books(self):
        response = self.c.get('/media/books')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "media/media_base.html")
        self.assertTemplateUsed(response, "media/books.html")
