from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from prayer.models import PrayerGroup, PrayerMessage


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

    def check_navbar(self, response, is_staff=False):
        """
        Navbar checks. Can be repeated throughout the app.
        is_staff parameter determines if staff-only items should be checked.
        """
        self.assertContains(response, "Home")
        if is_staff:
            self.assertContains(response, "Messages")
        self.assertContains(response, "Groups")
        self.assertContains(response, "Prayer Requests")
        self.assertContains(response, "People")
        # Previously asserted 'Navbar' text; remove as it isn't present in templates.

    def test_index_view(self):
        """
        Test index view showing public cards for anonymous users.
        Staff-only cards should not be visible.
        """
        client = TestPrayerModule.client
        response = client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.check_navbar(response, is_staff=False)
        # Staff-only cards should NOT be visible to anonymous users
        self.assertNotContains(response, "Create Message")
        self.assertNotContains(response, "Create Group")
        # Public cards should be visible
        self.assertContains(response, "Join Group")
        self.assertContains(response, "Submit Prayer Request")

    def test_index_view_staff_cards(self):
        """
        Test that staff-only cards (Create Message and Create Group)
        are visible to staff users.
        """
        client = TestPrayerModule.client
        # Create a staff user
        staff_user = User.objects.create_user(
            username="staffuser",
            password="StaffPass123!",
            email="staff@example.com",
            is_staff=True,
        )
        client.force_login(staff_user)
        response = client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.check_navbar(response, is_staff=True)
        # Staff-only cards should be visible
        self.assertContains(response, "Create Message")
        self.assertContains(response, "Create Group")
        # Public cards should also be visible
        self.assertContains(response, "Join Group")
        self.assertContains(response, "Submit Prayer Request")

    def test_new_message(self):
        """
        Tests New Message view - should be staff-only.
        """
        client = TestPrayerModule.client
        # Without login, should redirect
        response = client.get("/prayer/new-message")
        self.assertEqual(response.status_code, 302)

        # With regular user login, should still be blocked (staff only)
        user = User.objects.get(id=1)
        client.force_login(user)

        # Only staff can access
        if not user.is_staff:
            response = client.get("/prayer/new-message")
            self.assertIn(response.status_code, [302, 403])
        else:
            response = client.get("/prayer/new-message")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertContains(response, "Create a new message")
            self.assertTemplateUsed("new_message.html")

    def test_groups_view(self):
        """
        Test that groups view is staff-only.
        """
        client = TestPrayerModule.client
        # Without login, should redirect
        response = client.get("/prayer/groups")
        self.assertEqual(response.status_code, 302)

        # With regular user, should be blocked (staff only)
        user = User.objects.get(id=1)
        client.force_login(user)

        # Only staff can access
        if not user.is_staff:
            response = client.get("/prayer/groups")
            self.assertIn(response.status_code, [302, 403])
        else:
            response = client.get("/prayer/groups")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertContains(response, "Groups")
            self.assertTemplateUsed("groups.html")


class TestAccessControl(TestCase):
    """
    Comprehensive access control tests for all prayer app views.
    Ensures proper authentication and authorization for all endpoints.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test users for access control testing."""
        super().setUpClass()
        cls.regular_user = User.objects.create_user(
            username="regularuser",
            password="RegularPass123!",
            email="regular@example.com",
            is_staff=False,
        )
        cls.staff_user = User.objects.create_user(
            username="staffuser",
            password="StaffPass123!",
            email="staff@example.com",
            is_staff=True,
        )

    def test_public_views_accessible_without_login(self):
        """
        Test that public views (index, public_signup) are accessible
        without authentication.
        """
        client = Client()

        # Test index view
        response = client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Test public signup view
        response = client.get("/prayer/signup")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_views_require_login(self):
        """
        Test that authenticated views redirect to login when accessed
        without authentication.
        """
        client = Client()

        # Views that should require login
        protected_urls = [
            "/prayer/new-message",
            "/prayer/groups",
            "/prayer/send-message/1",
            "/prayer/group/detail/1",
            "/prayer/groups/delete/1",
            "/prayer/prayer-requests",
            "/prayer/delete_prayer_request/1",
            "/prayer/prayer-requests/mark-important/1",
            "/prayer/prayer-requests/mark-complete/1",
            "/prayer/prayer-requests/answer/1",
            "/prayer/people",
            "/prayer/delete-person/1",
            "/prayer/permissions/1",
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = client.get(url)
                # Should redirect to login (302) or 404 if object doesn't exist
                self.assertIn(
                    response.status_code,
                    [302, 404],
                    f"{url} should require login but returned {response.status_code}",
                )
                # If it's a redirect, verify it redirects to login page
                if response.status_code == 302:
                    self.assertIn("login", response.url.lower())

    def test_staff_views_accessible_by_staff(self):
        """
        Test that staff-only views (new_message, groups) are accessible
        to staff users.
        """
        client = Client()
        client.force_login(self.staff_user)

        # Test new_message view (staff only)
        response = client.get("/prayer/new-message")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Test groups view (staff only)
        response = client.get("/prayer/groups")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_message_page_explains_redirect_to_detail_workflow(self):
        """New message page should direct staff into the message detail workflow."""
        client = Client()
        client.force_login(self.staff_user)

        response = client.get("/prayer/new-message")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "message details page")
        self.assertContains(response, "Save and continue")

    def test_staff_views_blocked_for_regular_users(self):
        """
        Test that staff-only views (new_message, groups) are blocked
        for regular authenticated users who are not staff.
        """
        client = Client()
        client.force_login(self.regular_user)

        # Test new_message view - should redirect (403 or 302)
        response = client.get("/prayer/new-message")
        self.assertIn(
            response.status_code,
            [302, 403],
            "new_message should be blocked for non-staff users",
        )

        # Test groups view - should redirect (403 or 302)
        response = client.get("/prayer/groups")
        self.assertIn(
            response.status_code,
            [302, 403],
            "groups should be blocked for non-staff users",
        )

    def test_authenticated_views_accessible_by_authenticated_users(self):
        """
        Test that authenticated views are accessible to logged-in users.
        """
        client = Client()
        client.force_login(self.regular_user)

        # These views should be accessible to any authenticated user
        # (excluding staff-only views)
        accessible_urls = [
            "/prayer/prayer-requests",
            "/prayer/people",
        ]

        for url in accessible_urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f"{url} should be accessible to authenticated users",
                )

    def test_people_page_shows_privacy_and_terms_links(self):
        """People page should show Privacy Policy and Terms links near add person form."""
        client = Client()
        client.force_login(self.regular_user)

        response = client.get("/prayer/people")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, f'href="{reverse("core_app:privacy_policy")}"')
        self.assertContains(response, f'href="{reverse("core_app:terms_of_service")}"')
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms and Conditions")
        self.assertContains(response, "By adding yourself, you agree to our")

    def test_message_detail_requires_authentication(self):
        """
        Test that message_detail view requires authentication and staff status.
        """
        from prayer.models import PrayerMessage

        # Create a test message
        message = PrayerMessage.objects.create(
            subject="Test Message", message="Test content", name="Test User"
        )

        client = Client()

        # Test without login - should redirect to login
        response = client.get(f"/prayer/message-detail/{message.id}")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url.lower())

        # Test with regular (non-staff) user - should also be redirected (staff only)
        client.force_login(self.regular_user)
        response = client.get(f"/prayer/message-detail/{message.id}")
        self.assertIn(response.status_code, [302, 403])

        # Test with staff - should work
        client.force_login(self.staff_user)
        response = client.get(f"/prayer/message-detail/{message.id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)


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
            is_staff=True,  # Make this user staff for form testing
        )

    def test_new_message_form(self):
        """ """
        user = User.objects.get(id=1)
        client = TestPrayerForms.client
        client.force_login(user)
        endpoint = "/prayer/new-message"

        # Tests that valid data submits successfully (should redirect after save).
        data = {
            "name": "Prayer Request 8/30/2022",
            "subject": "Today's Requests",
            "message": "These are today's prayer requests.",
        }
        response = client.post(endpoint, data)
        self.assertEqual(response.status_code, 302)
        created_message = PrayerMessage.objects.get(name="Prayer Request 8/30/2022")
        self.assertRedirects(response, f"/prayer/message-detail/{created_message.id}")

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

        self.assertTrue(
            PrayerMessage.objects.filter(
                subject=data["subject"], message=data["message"]
            ).exists()
        )
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

        # Create two regular (non-staff) users for this test
        user_a = AuthUser.objects.create_user(
            username="user_a_regular", password="pw123", is_staff=False
        )
        user_b = AuthUser.objects.create_user(
            username="user_b_regular", password="pw456", is_staff=False
        )

        # Create messages for each user
        pm_a = PrayerMessage.objects.create(
            subject="Subject A",
            message="from A",
            name=user_a.username,
            submitted_by=user_a,
        )
        pm_b = PrayerMessage.objects.create(
            subject="Subject B",
            message="from B",
            name=user_b.username,
            submitted_by=user_b,
        )

        client = TestPrayerForms.client

        # Regular user (user_a) should see only their message
        client.force_login(user_a)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Subject A")
        self.assertNotContains(resp, "Subject B")

        # Staff user should see both
        staff = AuthUser.objects.create_user(username="staff_test", password="pwstaff")
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
        pm = PrayerMessage.objects.create(
            subject="ToDelete",
            message="Will be deleted",
            name=user_a.username,
            submitted_by=user_a,
        )

        # Create staff
        staff = AuthUser.objects.create_user(username="staff2", password="pwstaff")
        staff.is_staff = True
        staff.save()

        client = TestPrayerForms.client
        client.force_login(staff)

        # Answer the request
        resp = client.post(
            f"/prayer/prayer-requests/answer/{pm.id}", {"answer": "Answered!"}
        )
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
        self.assertTrue(hasattr(self.person_with_consent, "sms_consent"))
        self.assertTrue(hasattr(self.person_with_consent, "sms_consent_date"))

    def test_person_form_includes_consent_field(self):
        """Test that NewPersonForm includes sms_consent field."""
        from prayer.forms import NewPersonForm

        form = NewPersonForm()
        self.assertIn("sms_consent", form.fields)


class TestPublicSignup(TestCase):
    """Test public signup functionality for SMS opt-in."""

    client = Client()

    def test_public_signup_accessible_without_login(self):
        """Public signup page should be visible without authentication."""
        response = self.client.get("/prayer/signup")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Join Our Prayer Group")
        self.assertContains(response, "Please")
        self.assertContains(response, "create an account")
        self.assertContains(response, "log in")
        self.assertContains(response, "disabled")

    def test_public_signup_post_blocked_for_anonymous_user(self):
        """Anonymous users cannot submit signup form data."""
        from prayer.models import Person

        initial_count = Person.objects.count()
        data = {
            "first_name": "Anon",
            "last_name": "User",
            "phone_number": "+15555550123",
            "email": "anon@example.com",
        }

        response = self.client.post("/prayer/signup", data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Person.objects.count(), initial_count)
        self.assertContains(
            response,
            "Please sign up for an account and log in before joining SMS prayer updates.",
        )

    def test_public_signup_form_valid_submission_requires_login(self):
        """Authenticated users can submit and create a Person with SMS consent."""
        from prayer.models import Person

        self.client.force_login(
            User.objects.create_user(
                "signupuser", "signup@example.com", "StrongPass123!"
            )
        )

        initial_count = Person.objects.count()

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+12345678900",
            "email": "john@example.com",
        }

        response = self.client.post("/prayer/signup", data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Person.objects.count(), initial_count + 1)
        person = Person.objects.latest("id")
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.phone_number, "+12345678900")
        self.assertTrue(person.sms_consent)
        self.assertIsNotNone(person.sms_consent_date)

    def test_public_signup_form_missing_required_fields(self):
        """Authenticated submissions with missing fields should not create Person."""
        from prayer.models import Person

        self.client.force_login(
            User.objects.create_user(
                "signupuser2", "signup2@example.com", "StrongPass123!"
            )
        )

        initial_count = Person.objects.count()

        data = {
            "first_name": "Jane",
            "last_name": "",
            "phone_number": "+12345678901",
        }

        response = self.client.post("/prayer/signup", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.count(), initial_count)
        self.assertContains(response, "There was a problem with your submission")

    def test_public_signup_requires_phone_number(self):
        """Authenticated submissions without phone should not create Person."""
        from prayer.models import Person

        self.client.force_login(
            User.objects.create_user(
                "signupuser3", "signup3@example.com", "StrongPass123!"
            )
        )

        initial_count = Person.objects.count()

        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "",
            "email": "jane@example.com",
        }

        response = self.client.post("/prayer/signup", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.count(), initial_count)
        self.assertContains(response, "There was a problem with your submission")

    def test_public_signup_allows_optional_email(self):
        """Email field should be optional during authenticated signup."""
        from prayer.models import Person

        self.client.force_login(
            User.objects.create_user(
                "signupuser4", "signup4@example.com", "StrongPass123!"
            )
        )

        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+12345678901",
        }

        response = self.client.post("/prayer/signup", data)
        self.assertEqual(response.status_code, 302)

        person = Person.objects.latest("id")
        self.assertEqual(person.first_name, "Jane")
        self.assertTrue(person.email is None or person.email == "")

    def test_index_links_to_public_signup(self):
        """Index page should link to public signup, not the staff people page."""
        response = self.client.get("/prayer/index")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "href=\"{% url 'prayer:public_signup' %}\"".replace(
                "{% url 'prayer:public_signup' %}", "/prayer/signup"
            ),
        )


class TestPrayerRegression(TestCase):
    """Regression tests to ensure answered toggle text and aria attributes persist."""

    client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="reguser", password="pw", email="r@example.com"
        )
        from django.contrib.auth.models import User as AuthUser

        cls.staff = AuthUser.objects.create_user(
            username="regstaff", password="pwstaff"
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def test_unanswered_shows_mark_answered_and_aria_false(self):
        """Unanswered requests should show 'Mark Answered' and aria-pressed="false" for staff."""
        from prayer.models import PrayerMessage

        PrayerMessage.objects.create(
            subject="R1",
            message="please",
            name=self.user.username,
            submitted_by=self.user,
            is_completed=False,
        )
        client = TestPrayerRegression.client
        client.force_login(self.staff)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Mark Answered")
        self.assertContains(resp, 'aria-pressed="false"')

    def test_answered_shows_unmark_answered_and_aria_true(self):
        """Answered requests should show 'Unmark Answered' and aria-pressed="true" for staff."""
        from prayer.models import PrayerMessage

        PrayerMessage.objects.create(
            subject="R2",
            message="thanks",
            name=self.user.username,
            submitted_by=self.user,
            is_completed=True,
        )
        client = TestPrayerRegression.client
        client.force_login(self.staff)
        resp = client.get("/prayer/prayer-requests")
        self.assertContains(resp, "Unmark Answered")
        self.assertContains(resp, 'aria-pressed="true"')

    def test_toggle_complete_endpoint_toggles_is_completed(self):
        """POSTing to the toggle_complete endpoint should flip `is_completed`."""
        from prayer.models import PrayerMessage

        pm = PrayerMessage.objects.create(
            subject="TC1",
            message="tc",
            name=self.user.username,
            submitted_by=self.user,
            is_completed=False,
        )
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

        pm = PrayerMessage.objects.create(
            subject="TI1",
            message="ti",
            name=self.user.username,
            submitted_by=self.user,
            is_important=False,
        )
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

        pm = PrayerMessage.objects.create(
            subject="A1", message="ans", name=self.user.username, submitted_by=self.user
        )
        client = TestPrayerRegression.client
        client.force_login(self.staff)

        resp = client.post(
            f"/prayer/prayer-requests/answer/{pm.id}", {"answer": "Got it"}
        )
        self.assertEqual(resp.status_code, 302)
        pm.refresh_from_db()
        self.assertEqual(pm.answer_text, "Got it")
        self.assertIsNotNone(pm.answered_at)


class TestPrayerLegalLinks(TestCase):
    """Tests for privacy policy and terms links in prayer app UI."""

    def test_public_signup_includes_privacy_and_terms_links(self):
        client = Client()
        response = client.get("/prayer/signup")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms and Conditions")
        self.assertContains(response, "/core_app/privacy-policy/")
        self.assertContains(response, "/core_app/terms-of-service/")


class TestSMSLogging(TestCase):
    """
    Tests for the SMSLog model, message-group association,
    and deduplication logic in the message_detail view.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = User.objects.create_user(
            username="smslogstaff",
            password="pw",
            email="smslogstaff@example.com",
            is_staff=True,
        )

    def setUp(self):
        from prayer.models import PrayerGroup, PrayerMessage, Person

        self.group_a = PrayerGroup.objects.create(name="Group A", short_description="A")
        self.group_b = PrayerGroup.objects.create(name="Group B", short_description="B")

        # Person in both groups — should only receive one message
        self.person_both = Person.objects.create(
            first_name="Alice",
            last_name="Smith",
            phone_number="+10000000001",
            sms_consent=True,
        )
        # Person in group_a only
        self.person_a = Person.objects.create(
            first_name="Bob",
            last_name="Jones",
            phone_number="+10000000002",
            sms_consent=True,
        )
        # Person without consent
        self.person_no_consent = Person.objects.create(
            first_name="Carol",
            last_name="White",
            phone_number="+10000000003",
            sms_consent=False,
        )

        self.group_a.people.add(self.person_both, self.person_a, self.person_no_consent)
        self.group_b.people.add(self.person_both)

        self.message = PrayerMessage.objects.create(
            name="Test Sender",
            subject="Test Subject",
            message="Hello, this is a test.",
        )

    def test_smslog_created_on_send(self):
        """
        Posting to message_detail with SMSMessage mocked should create
        an SMSLog entry for each consented recipient.
        """
        from unittest.mock import patch, MagicMock
        from prayer.models import SMSLog

        client = Client()
        client.force_login(self.staff)

        with patch("prayer.views.SMSMessage") as MockSMS:
            instance = MagicMock()
            instance.send.return_value = {
                self.person_both: (True, ""),
                self.person_a: (True, ""),
            }
            MockSMS.return_value = instance

            response = client.post(
                f"/prayer/message-detail/{self.message.id}",
                {"groups": [self.group_a.name, self.group_b.name]},
            )

        self.assertEqual(response.status_code, 302)
        logs = SMSLog.objects.filter(message=self.message)
        self.assertEqual(logs.count(), 2)
        self.assertTrue(all(log.success for log in logs))
        self.assertTrue(all(log.sent_by == self.staff for log in logs))

    def test_deduplication_person_in_two_groups_gets_one_log(self):
        """
        A person who belongs to two selected groups should appear in only
        one SMSLog entry (the set deduplication guarantees one send).
        """
        from unittest.mock import patch, MagicMock
        from prayer.models import SMSLog

        client = Client()
        client.force_login(self.staff)

        with patch("prayer.views.SMSMessage") as MockSMS:
            instance = MagicMock()
            # Both groups share person_both; mock returns one entry for them
            instance.send.return_value = {
                self.person_both: (True, ""),
            }
            MockSMS.return_value = instance

            client.post(
                f"/prayer/message-detail/{self.message.id}",
                {"groups": [self.group_a.name, self.group_b.name]},
            )

        logs = SMSLog.objects.filter(message=self.message, recipient=self.person_both)
        self.assertEqual(logs.count(), 1)

    def test_failed_send_logged_with_error(self):
        """
        When a send fails, the SMSLog entry should record success=False
        and include the error message.
        """
        from unittest.mock import patch, MagicMock
        from prayer.models import SMSLog

        client = Client()
        client.force_login(self.staff)

        error_text = "Twilio error: invalid number"

        with patch("prayer.views.SMSMessage") as MockSMS:
            instance = MagicMock()
            instance.send.return_value = {
                self.person_a: (False, error_text),
            }
            MockSMS.return_value = instance

            client.post(
                f"/prayer/message-detail/{self.message.id}",
                {"groups": [self.group_a.name]},
            )

        log = SMSLog.objects.get(message=self.message, recipient=self.person_a)
        self.assertFalse(log.success)
        self.assertEqual(log.error_message, error_text)

    def test_no_consented_recipients_creates_no_log(self):
        """
        Selecting a group where nobody has consented should produce no
        SMSLog entries.
        """
        from prayer.models import SMSLog, PrayerGroup, Person

        group_c = PrayerGroup.objects.create(
            name="No Consent Group", short_description="C"
        )
        group_c.people.add(self.person_no_consent)

        client = Client()
        client.force_login(self.staff)

        response = client.post(
            f"/prayer/message-detail/{self.message.id}",
            {"groups": [group_c.name]},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SMSLog.objects.filter(message=self.message).count(), 0)

    def test_message_groups_m2m_saved_on_send(self):
        """
        After posting to message_detail, the selected groups should be
        persisted on the PrayerMessage.groups M2M field.
        """
        from unittest.mock import patch, MagicMock

        client = Client()
        client.force_login(self.staff)

        with patch("prayer.views.SMSMessage") as MockSMS:
            instance = MagicMock()
            instance.send.return_value = {self.person_both: (True, "")}
            MockSMS.return_value = instance

            client.post(
                f"/prayer/message-detail/{self.message.id}",
                {"groups": [self.group_a.name]},
            )

        self.message.refresh_from_db()
        self.assertIn(self.group_a, self.message.groups.all())
        self.assertNotIn(self.group_b, self.message.groups.all())

    def test_message_detail_requires_staff(self):
        """
        Non-staff authenticated users should be redirected away from
        the message_detail view.
        """
        regular = User.objects.create_user(
            username="smsregular", password="pw", email="smsreg@example.com"
        )
        client = Client()
        client.force_login(regular)

        response = client.get(f"/prayer/message-detail/{self.message.id}")
        self.assertIn(response.status_code, [302, 403])

    def test_smslog_str(self):
        """SMSLog __str__ should include OK/FAIL and recipient name."""
        from prayer.models import SMSLog

        log_ok = SMSLog.objects.create(
            message=self.message,
            recipient=self.person_a,
            success=True,
            sent_by=self.staff,
        )
        log_fail = SMSLog.objects.create(
            message=self.message,
            recipient=self.person_a,
            success=False,
            error_message="oops",
            sent_by=self.staff,
        )
        self.assertIn("OK", str(log_ok))
        self.assertIn("FAIL", str(log_fail))
        self.assertIn("Bob", str(log_ok))

    def test_new_message_form_redirect_preserves_selected_groups(self):
        """
        Groups selected during message creation should still be selected on the
        detail page after the redirect.
        """
        client = Client()
        client.force_login(self.staff)
        response = client.post(
            "/prayer/new-message",
            {
                "name": "Grouped Sender",
                "subject": "Grouped Subject",
                "message": "Grouped message.",
                "groups": [self.group_a.id, self.group_b.id],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'value="Group A" checked')
        self.assertContains(response, 'value="Group B" checked')
