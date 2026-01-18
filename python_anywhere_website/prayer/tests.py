from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase


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
        User.objects.create_user(
            username="bama",
            password="FortheWin!$",
            email="bbgenius@geniusbar.com",
        )

    def check_navbar(self, response):
        """
        Navbar checks. Can be repeated throughout the app.
        """
        self.assertContains(response, "Home")
        self.assertContains(response, "Messages")
        self.assertContains(response, "Groups")
        self.assertContains(response, "Prayer Requests")
        self.assertContains(response, "People")
        # Previously asserted 'Navbar' text; remove as it isn't present in templates.

    def test_index_view(self):
        """
        Need to add item to DB to allow it to work?
        """
        client = TestPrayerModule.client
        response = client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.check_navbar(response)
        # Updated cards: Create Message, Create Group, Join Group, Submit Prayer Request
        self.assertContains(response, "Create Message")
        self.assertContains(response, "Create Group")
        self.assertContains(response, "Join Group")
        self.assertContains(response, "Submit Prayer Request")

    def test_new_message(self):
        """
        Tests New Message view.
        """
        client = TestPrayerModule.client
        response = client.get("/prayer/new-message")
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(id=1)
        client.force_login(user)
        response = client.get("/prayer/new-message")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertContains(response, "Create a new message")
        self.assertTemplateUsed("new_message.html")

    def test_groups_view(self):
        """
        Test that this view is login protected.
        Test that this view is accessible when logged in.
        Test that this view contains...
        """
        client = TestPrayerModule.client
        response = client.get("/prayer/groups")
        self.assertEqual(response.status_code, 302)  # Check to ensure login is required

        user = User.objects.get(id=1)
        client.force_login(user)
        response = client.get("/prayer/groups")
        self.assertEqual(response.status_code, HTTPStatus.OK)  # Check works with login

        self.assertContains(response, "Groups")
        self.assertContains(response, "Name")
        self.assertContains(response, "Description")
        self.assertContains(response, "New Group")
        self.assertContains(response, "Name")
        self.assertContains(response, "Short description")
        self.assertContains(response, "Long description")
        self.assertContains(response, "Submit")

        self.assertTemplateUsed("groups.html")

        # Will add when PrayerGroup has been added to the test db.
        # self.assertContains(response, 'Details')
        # self.assertContains(response, 'Delete')


class TestPrayerForms(TestCase):
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
        User.objects.create_user(
            username="bama",
            password="FortheWin!$",
            email="bbgenius@geniusbar.com",
        )

    def test_new_message_form(self):
        """ """
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/new-message"

        # Tests that valid data submits successfully.
        data = {
            "name": "Prayer Request 8/30/2022",
            "subject": "Today's Requests",
            "message": "These are today's prayer requests.",
        }
        response = client.post(endpoint, data)
        self.assertEqual(response.status_code, 200)

        # Tests that form submission with missing data fails.
        data_1 = {
            "name": "",
            "subject": "This has",
            "message": "words",
        }

        data_2 = {
            "name": "This has",
            "subject": "",
            "message": "Words",
        }

        data_3 = {
            "name": "This has",
            "subject": "Words",
            "message": "",
        }

        data_list = [data_1, data_2, data_3]

        # Runs all tests that should fail.
        for data in data_list:
            self.assertRaises(
                ValueError,
                client.post,
                path=endpoint,
                data=data,
            )

    def test_new_person_form(self):
        """ """
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/people"

        # Test data that should submit successfully.
        data = {
            "first_name": "My",
            "last_name": "Name",
            "phone_number": "Is",
            "email": "This!",
        }

        # Should succeed.
        response = client.post(endpoint, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Test data that should fail.
        data_1 = {
            "first_name": "",
            "last_name": "This",
            "phone_number": "is",
            "email": "a test",
        }

        data_2 = {
            "first_name": "This",
            "last_name": "",
            "phone_number": "is",
            "email": "a test",
        }

        #  Should fail. TODO Why does this not raise an error?
        # self.assertRaises(
        #     ValueError,
        #     client.post,
        #     path=endpoint,
        #     data=data_1,
        # )

        # self.assertRaises(
        #     ValueError,
        #     client.post,
        #     path=endpoint,
        #     data=data_2
        # )

    def test_new_group_form(self):
        """ """
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/groups"

        response = client.post(endpoint)
        self.assertEqual(response.status_code, 200)

        data = {
            "name": "This",
            "short_description": "Is a ",
            "long_description": "Test",
        }

        client.post(endpoint, data)

        data_1 = {
            "name": "",
            "short_description": "Is a ",
            "long_description": "Test",
        }

        data_2 = {
            "name": "This",
            "short_description": "",
            "long_description": "Test",
        }

        data_3 = {
            "name": "This",
            "short_description": "Is a ",
            "long_description": "",
        }

        data_list = [data_1, data_2, data_3]

        # TODO Why does this not result in an error?
        # I should have to wrap the post request in assertRaises.
        for data in data_list:
            client.post(
                path=endpoint,
                data=data,
            )

    def test_prayer_request_form_valid_and_name_set(self):
        """Test that a valid prayer request is saved and name is taken from user."""
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/prayer-requests"

        data = {
            "subject": "Please pray for testing",
            "message": "This is a test prayer request",
        }

        response = client.post(endpoint, data)
        # View redirects on success
        self.assertEqual(response.status_code, 302)

        from prayer.models import PrayerMessage
        self.assertTrue(PrayerMessage.objects.filter(subject=data["subject"], message=data["message"]).exists())
        pm = PrayerMessage.objects.get(subject=data["subject"])
        # User in setUpClass has no first/last name, so name should equal username
        self.assertEqual(pm.name, user.username)

    def test_prayer_request_form_invalid_missing_fields(self):
        """Test that missing subject or message prevents saving and returns form with errors."""
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/prayer-requests"

        bad_cases = [
            {"subject": "", "message": "Has message"},
            {"subject": "Has subject", "message": ""},
        ]

        from prayer.models import PrayerMessage
        initial_count = PrayerMessage.objects.count()

        for data in bad_cases:
            response = client.post(endpoint, data)
            # Form should re-render with status 200 and not save
            self.assertEqual(response.status_code, 200)
            self.assertEqual(PrayerMessage.objects.count(), initial_count)

    def test_prayer_request_submission_logged_in_success(self):
        """Authenticated user can submit a prayer request successfully."""
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/prayer-requests"

        data = {"subject": "Login success test", "message": "Logged in user request."}
        response = client.post(endpoint, data)
        # Successful submissions redirect
        self.assertEqual(response.status_code, 302)

        from prayer.models import PrayerMessage
        self.assertTrue(PrayerMessage.objects.filter(subject=data["subject"]).exists())

    def test_prayer_request_submission_anonymous_blocked(self):
        """Anonymous POST to prayer requests should be redirected and not saved."""
        client = TestPrayerForms.client
        endpoint = "/prayer/prayer-requests"
        data = {"subject": "Anon test", "message": "Should not be saved"}

        from prayer.models import PrayerMessage
        initial_count = PrayerMessage.objects.count()

        response = client.post(endpoint, data)
        # Should redirect to login (302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PrayerMessage.objects.count(), initial_count)

    def test_staff_sees_all_requests_but_user_sees_own(self):
        """Create requests from two users and verify staff sees both while a regular user sees only their own."""
        from django.contrib.auth.models import User as AuthUser
        from prayer.models import PrayerMessage

        # Create two users
        user_a = User.objects.get(id=1)
        user_b = AuthUser.objects.create_user(username="other", password="pw")

        # Create messages for each user
        pm_a = PrayerMessage.objects.create(subject="Subject A", message="from A", name=user_a.username, submitted_by=user_a)
        pm_b = PrayerMessage.objects.create(subject="Subject B", message="from B", name=user_b.username, submitted_by=user_b)

        client = TestPrayerForms.client

        # Regular user (user_a) should see only their message
        client.force_login(user_a)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Subject A")
        self.assertNotContains(resp, "Subject B")

        # Staff user should see both
        staff = AuthUser.objects.create_user(username="staff", password="pwstaff")
        staff.is_staff = True
        staff.save()
        client.force_login(staff)
        resp2 = client.get("/prayer/prayer-requests")
        self.assertContains(resp2, "Subject A")
        self.assertContains(resp2, "Subject B")

    def test_staff_can_delete_and_answer_requests(self):
        """Staff can delete a request and save an answer."""
        from django.contrib.auth.models import User as AuthUser
        from prayer.models import PrayerMessage

        user_a = User.objects.get(id=1)
        pm = PrayerMessage.objects.create(subject="ToDelete", message="Will be deleted", name=user_a.username, submitted_by=user_a)

        # Create staff
        staff = AuthUser.objects.create_user(username="staff2", password="pwstaff")
        staff.is_staff = True
        staff.save()

        client = TestPrayerForms.client
        client.force_login(staff)

        # Answer the request
        resp = client.post(f"/prayer/prayer-requests/answer/{pm.id}", {"answer": "Answered!"})
        self.assertEqual(resp.status_code, 302)
        pm.refresh_from_db()
        self.assertEqual(pm.answer_text, "Answered!")

        # Delete the request
        resp2 = client.post(f"/prayer/prayer-requests/delete/{pm.id}")
        self.assertEqual(resp2.status_code, 302)
        self.assertFalse(PrayerMessage.objects.filter(id=pm.id).exists())

    def test_permissions_form(self):
        """ """
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/groups"

        data = {
            "may_send_emails": True,
            "may_send_sms": False,
        }

        data_1 = {"may_send_email": "", "may_send_sms": False}
        data_2 = {"may_send_email": True, "may_send_sms": "False"}
        data_list = [data_1, data_2]

        client.post(endpoint, data=data)

        # TODO Why doesn't this raise an error for invalid data?
        # for data in data_list:
        #     self.assertRaises(
        #         ValueError,
        #         client.post,
        #         path=endpoint,
        #         data=data,
        #     )


class TestSMSConsent(TestCase):
    """Test SMS consent functionality."""
    
    def setUp(self):
        """Set up test data."""
        from prayer.models import Person
        
        User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        
        # Create a person with SMS consent
        self.person_with_consent = Person.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+12345678900",
            email="john@example.com",
            sms_consent=True,
        )
        
        # Create a person without SMS consent
        self.person_without_consent = Person.objects.create(
            first_name="Jane",
            last_name="Smith",
            phone_number="+12345678901",
            email="jane@example.com",
            sms_consent=False,
        )
    
    def test_person_has_sms_consent_field(self):
        """Test that Person model has sms_consent field."""
        self.assertTrue(hasattr(self.person_with_consent, 'sms_consent'))
        self.assertTrue(hasattr(self.person_with_consent, 'sms_consent_date'))
    
    def test_person_form_includes_consent_field(self):
        """Test that NewPersonForm includes sms_consent field."""
        from prayer.forms import NewPersonForm
        form = NewPersonForm()
        self.assertIn('sms_consent', form.fields)


class TestPrayerRegression(TestCase):
    """Regression tests to ensure answered toggle text and aria attributes persist."""

    client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="reguser", password="pw", email="r@example.com")
        from django.contrib.auth.models import User as AuthUser
        cls.staff = AuthUser.objects.create_user(username="regstaff", password="pwstaff")
        cls.staff.is_staff = True
        cls.staff.save()

    def test_unanswered_shows_mark_answered_and_aria_false(self):
        """Unanswered requests should show 'Mark Answered' and aria-pressed="false" for staff."""
        from prayer.models import PrayerMessage

        PrayerMessage.objects.create(subject="R1", message="please", name=self.user.username, submitted_by=self.user, is_completed=False)
        client = TestPrayerRegression.client
        client.force_login(self.staff)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Mark Answered")
        self.assertContains(resp, 'aria-pressed="false"')

    def test_answered_shows_unmark_answered_and_aria_true(self):
        """Answered requests should show 'Unmark Answered' and aria-pressed="true" for staff."""
        from prayer.models import PrayerMessage

        PrayerMessage.objects.create(subject="R2", message="thanks", name=self.user.username, submitted_by=self.user, is_completed=True)
        client = TestPrayerRegression.client
        client.force_login(self.staff)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Unmark Answered")
        self.assertContains(resp, 'aria-pressed="true"')

    def test_toggle_complete_endpoint_toggles_is_completed(self):
        """POSTing to the toggle_complete endpoint should flip `is_completed`."""
        from prayer.models import PrayerMessage

        pm = PrayerMessage.objects.create(subject="TC1", message="tc", name=self.user.username, submitted_by=self.user, is_completed=False)
        client = TestPrayerRegression.client
        client.force_login(self.staff)

        resp = client.post(f"/prayer/prayer-requests/mark-complete/{pm.id}")
        self.assertEqual(resp.status_code, 302)
        pm.refresh_from_db()
        self.assertTrue(pm.is_completed)

        # toggle back
        resp2 = client.post(f"/prayer/prayer-requests/mark-complete/{pm.id}")
        self.assertEqual(resp2.status_code, 302)
        pm.refresh_from_db()
        self.assertFalse(pm.is_completed)

    def test_toggle_important_endpoint_toggles_is_important(self):
        """POSTing to the toggle_important endpoint should flip `is_important`."""
        from prayer.models import PrayerMessage

        pm = PrayerMessage.objects.create(subject="TI1", message="ti", name=self.user.username, submitted_by=self.user, is_important=False)
        client = TestPrayerRegression.client
        client.force_login(self.staff)

        resp = client.post(f"/prayer/prayer-requests/mark-important/{pm.id}")
        self.assertEqual(resp.status_code, 302)
        pm.refresh_from_db()
        self.assertTrue(pm.is_important)

        resp2 = client.post(f"/prayer/prayer-requests/mark-important/{pm.id}")
        self.assertEqual(resp2.status_code, 302)
        pm.refresh_from_db()
        self.assertFalse(pm.is_important)

    def test_answer_endpoint_sets_answered_at(self):
        """Posting an answer should set `answer_text` and `answered_at`."""
        from prayer.models import PrayerMessage
        import datetime

        pm = PrayerMessage.objects.create(subject="A1", message="ans", name=self.user.username, submitted_by=self.user)
        client = TestPrayerRegression.client
        client.force_login(self.staff)

        resp = client.post(f"/prayer/prayer-requests/answer/{pm.id}", {"answer": "Got it"})
        self.assertEqual(resp.status_code, 302)
        pm.refresh_from_db()
        self.assertEqual(pm.answer_text, "Got it")
        self.assertIsNotNone(pm.answered_at)

