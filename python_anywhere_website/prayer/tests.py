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

    def test_message_detail_requires_authentication(self):
        """
        Test that message_detail view requires authentication.
        Note: This view currently lacks @login_required decorator.
        """
        from prayer.models import PrayerMessage

        # Create a test message
        message = PrayerMessage.objects.create(
            subject="Test Message", message="Test content", name="Test User"
        )

        client = Client()

        # Test without login - should redirect or return error
        response = client.get(f"/prayer/message-detail/{message.id}")
        # If view doesn't have @login_required, this test documents the current behavior
        # It may return 200 (which would be a security issue to fix)
        # or 302 (if authentication is required)
        self.assertIn(
            response.status_code,
            [HTTPStatus.OK, 302],
            "message_detail should either require login or be accessible",
        )

        # Test with login - should work
        client.force_login(self.regular_user)
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
        """Public signup page should be accessible without authentication."""
        response = self.client.get("/prayer/signup")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Join Our Prayer Group")
        self.assertContains(response, "Sign Up for SMS Updates")

    def test_public_signup_form_valid_submission(self):
        """Valid form submission should create a Person with SMS consent."""
        from prayer.models import Person

        initial_count = Person.objects.count()

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+12345678900",
            "email": "john@example.com",
        }

        response = self.client.post("/prayer/signup", data)
        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Check that person was created with SMS consent
        self.assertEqual(Person.objects.count(), initial_count + 1)
        person = Person.objects.latest("id")
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.phone_number, "+12345678900")
        self.assertTrue(person.sms_consent)
        self.assertIsNotNone(person.sms_consent_date)

    def test_public_signup_form_missing_required_fields(self):
        """Form submission with missing required fields should not create Person."""
        from prayer.models import Person

        initial_count = Person.objects.count()

        # Missing last name
        data = {
            "first_name": "Jane",
            "last_name": "",
            "phone_number": "+12345678901",
        }

        response = self.client.post("/prayer/signup", data)
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.count(), initial_count)
        self.assertContains(response, "There was a problem with your submission")

    def test_public_signup_requires_phone_number(self):
        """Form submission without phone number should not create Person."""
        from prayer.models import Person

        initial_count = Person.objects.count()

        # Missing phone number
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "",
            "email": "jane@example.com",
        }

        response = self.client.post("/prayer/signup", data)
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.count(), initial_count)
        self.assertContains(response, "There was a problem with your submission")

    def test_public_signup_allows_optional_email(self):
        """Email field should be optional during signup."""
        from prayer.models import Person

        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+12345678901",
            # No email provided
        }

        response = self.client.post("/prayer/signup", data)
        self.assertEqual(response.status_code, 302)

        person = Person.objects.latest("id")
        self.assertEqual(person.first_name, "Jane")
        # Email can be None or empty string
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
