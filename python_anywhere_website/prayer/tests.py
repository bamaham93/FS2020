from django.test import TestCase, TransactionTestCase
from django.test import Client

# from django.contrib.auth.models import User
from http import HTTPStatus


# Create your tests here.
class TestPrayerModule(TestCase):
    """
    View tests for the prayer module.
    """

    client = Client()

    @classmethod
    def setUpClass(cls):
        """
        Inserts at least one item into each of the database tables for testing.
        Performed once for the entire class.
        """
        super().setUpClass()

    def check_navbar(self, response):
        """
        Navbar checks. Can be repeated throughout the app.
        """
        self.assertContains(response, "Home")
        self.assertContains(response, "New Message")
        self.assertContains(response, "Groups")
        self.assertContains(response, "Prayer Requests")
        self.assertContains(response, "People")
        self.assertContains(response, "Navbar")

    def test_index_view(self):
        """ """
        client = TestPrayerModule.client
        response = client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.check_navbar(response)

        self.assertContains(response, "Text Messaging")
        self.assertContains(response, "Email")
        self.assertContains(response, "Submit Prayer Request")

    def test_new_message(self):
        """
        Tests New Message view.
        """
        client = TestPrayerModule.client
        response = client.get("/prayer/new-message")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertContains(response, "Create a new message")

    def test_groups_view(self):
        """ """
        client = TestPrayerModule.client
        response = client.get("/prayer/groups")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertContains(response, "Groups")
        self.assertContains(response, "Name")
        self.assertContains(response, "Description")
        self.assertContains(response, "New Group")
        self.assertContains(response, "Name")
        self.assertContains(response, "Short description")
        self.assertContains(response, "Long description")
        self.assertContains(response, "Submit")

        # Will add when PrayerGroup has been added to the test db.
        # self.assertContains(response, 'Details')
        # self.assertContains(response, 'Delete')
