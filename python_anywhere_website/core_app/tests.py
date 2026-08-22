from django.test import TestCase
from django.contrib.auth.models import User


class SanityTests(TestCase):
    def test_root_redirects_to_index(self):
        resp = self.client.get("/")
        # redirect to core_app:index
        self.assertIn(resp.status_code, (302, 301))

    def test_fs2020_index_available(self):
        resp = self.client.get("/fs2020/index")
        self.assertEqual(resp.status_code, 200)

    def test_admin_login_page_available(self):
        resp = self.client.get("/admin/login/")
        # admin login page should be accessible
        self.assertIn(resp.status_code, (200, 302))


class AuthFlowTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "s3cretpass"
        self.user = User.objects.create_user(
            self.username, "test@example.com", self.password
        )

    def test_protected_view_redirects_when_anonymous(self):
        resp = self.client.get("/fs2020/aircraft/add/")
        # should redirect to login
        self.assertIn(resp.status_code, (302, 301))

    def test_protected_view_accessible_after_login(self):
        login_success = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(login_success)
        resp = self.client.get("/fs2020/aircraft/add/")
        self.assertEqual(resp.status_code, 200)

    def test_login_view_works(self):
        # use the login URL provided by django.contrib.auth at /core_app/login/
        resp = self.client.post(
            "/core_app/login/",
            {"username": self.username, "password": self.password},
            follow=True,
        )
        # after successful login should be authenticated
        if resp.context:
            user = resp.context.get("user")
            self.assertTrue(user.is_authenticated)
        else:
            # follow=True may redirect to external, so at least ensure response is 200
            self.assertEqual(resp.status_code, 200)


class SignUpTests(TestCase):
    """Tests for the A2P-compliant signup form."""

    def test_signup_page_accessible(self):
        """Test that the signup page is accessible."""
        resp = self.client.get("/core_app/signup/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Signup")
        self.assertContains(resp, "SMS Messaging Consent")

    def test_signup_form_has_required_fields(self):
        """Test that the signup form has all required A2P fields."""
        resp = self.client.get("/core_app/signup/")
        self.assertContains(resp, "phone_number")
        self.assertContains(resp, "sms_consent")
        self.assertContains(resp, "STOP")  # Check for opt-out language

    def test_signup_creates_user_without_phone(self):
        """Test that signup works without providing phone number."""
        data = {
            "username": "testuser2",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        resp = self.client.post("/core_app/signup/", data, follow=True)
        self.assertTrue(User.objects.filter(username="testuser2").exists())

    def test_signup_creates_person_with_consent(self):
        """Test that signup creates a Person record when phone and consent are provided."""
        from prayer.models import Person

        data = {
            "username": "testuser3",
            "first_name": "Test",
            "last_name": "User",
            "email": "test3@example.com",
            "phone_number": "+12345678900",
            "sms_consent": True,
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        resp = self.client.post("/core_app/signup/", data, follow=True)
        self.assertTrue(User.objects.filter(username="testuser3").exists())
        person = Person.objects.filter(phone_number="+12345678900").first()
        self.assertIsNotNone(person)
        self.assertTrue(person.sms_consent)
        self.assertIsNotNone(person.sms_consent_date)


class NavbarAccountsTests(TestCase):
    """Tests for the accounts dropdown in the navbar."""

    def test_navbar_shows_login_and_signup_when_anonymous(self):
        """Test that unauthenticated users see Login and Signup in navbar."""
        resp = self.client.get("/")
        # follow redirects to get to the page with navbar
        resp = self.client.get(resp.url if resp.status_code in (301, 302) else "/")
        self.assertContains(resp, "Accounts")
        self.assertContains(resp, "/core_app/login/")
        self.assertContains(resp, "/core_app/signup/")
        self.assertNotContains(resp, "/core_app/logout/")

    def test_navbar_shows_logout_when_authenticated(self):
        """Test that authenticated users see Logout in navbar."""
        user = User.objects.create_user("testuser", "test@example.com", "password123")
        self.client.login(username="testuser", password="password123")
        resp = self.client.get("/")
        # follow redirects to get to the page with navbar
        if resp.status_code in (301, 302):
            resp = self.client.get(resp.url, follow=True)
        self.assertContains(resp, "Accounts")
        self.assertContains(resp, "/core_app/logout/")
        self.assertNotContains(resp, "/core_app/login/")
        self.assertNotContains(resp, "/core_app/signup/")

    def test_navbar_shows_admin_link_for_staff_users(self):
        """Test that staff users see Admin link in navbar."""
        user = User.objects.create_user("staffuser", "staff@example.com", "password123")
        user.is_staff = True
        user.save()
        self.client.login(username="staffuser", password="password123")
        resp = self.client.get("/")
        # follow redirects to get to the page with navbar
        if resp.status_code in (301, 302):
            resp = self.client.get(resp.url, follow=True)
        self.assertContains(resp, "Accounts")
        self.assertContains(resp, "/admin/")
        self.assertContains(resp, "/core_app/logout/")

    def test_navbar_no_admin_link_for_non_staff_users(self):
        """Test that non-staff users don't see Admin link in navbar."""
        user = User.objects.create_user(
            "regularuser", "regular@example.com", "password123"
        )
        self.client.login(username="regularuser", password="password123")
        resp = self.client.get("/")
        # follow redirects to get to the page with navbar
        if resp.status_code in (301, 302):
            resp = self.client.get(resp.url, follow=True)
        self.assertContains(resp, "Accounts")
        # Should not have admin link in dropdown (checking the dropdown item, not just /admin/ in page)
        # We check that /admin/ is not in dropdown-item with Admin text
        content = resp.content.decode("utf-8")
        # Make sure there's no dropdown-item with href="/admin/"
        self.assertNotIn('dropdown-item" href="/admin/"', content)




class PublicAccessTests(TestCase):
    """Ensure policy and signup pages stay public without authentication."""

    def test_signup_page_does_not_redirect_to_login(self):
        resp = self.client.get("/core_app/signup/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'name="next"')

    def test_privacy_policy_does_not_redirect_to_login(self):
        resp = self.client.get("/core_app/privacy-policy/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'name="next"')

    def test_terms_page_does_not_redirect_to_login(self):
        resp = self.client.get("/core_app/terms-of-service/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'name="next"')

class CompliancePolicyTests(TestCase):
    """Tests for Twilio/A2P privacy and opt-in compliance copy."""

    def test_privacy_policy_page_available(self):
        resp = self.client.get("/core_app/privacy-policy/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Privacy Policy")

    def test_privacy_policy_includes_required_twilio_disclosures(self):
        resp = self.client.get("/core_app/privacy-policy/")
        self.assertContains(resp, "what information")
        self.assertContains(resp, "How We Use Information")
        self.assertContains(
            resp,
            "We do not share your phone number, SMS consent, or messaging data with third parties for"
        )
        self.assertContains(resp, "marketing or promotional purposes")
        self.assertContains(resp, "STOP")

    def test_signup_page_has_compliant_web_opt_in_statement(self):
        resp = self.client.get("/core_app/signup/")
        self.assertContains(resp, "By providing your phone number, you agree to receive text messages")
        self.assertContains(resp, "Message and data")
        self.assertContains(resp, "Message frequency varies")
        self.assertContains(resp, "Reply")
        self.assertContains(resp, "Privacy Policy")
        self.assertContains(resp, "Terms of Service")

    def test_terms_of_service_page_available(self):
        resp = self.client.get("/core_app/terms-of-service/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "FS2020 Alerts SMS Terms of Service")
        self.assertContains(resp, "Program Description")
        self.assertContains(resp, "Cancellation / Opt-Out")
        self.assertContains(resp, "Text <strong>STOP</strong>", html=True)
        self.assertContains(resp, "Reply <strong>HELP</strong>", html=True)
        self.assertContains(resp, "Carriers are not liable for delayed or undelivered messages")
        self.assertContains(resp, "Message frequency varies")
