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
		self.user = User.objects.create_user(self.username, "test@example.com", self.password)

	def test_protected_view_redirects_when_anonymous(self):
		resp = self.client.get("/fs2020/aircraft/add/")
		# should redirect to login
		self.assertIn(resp.status_code, (302, 301))

	def test_protected_view_accessible_after_login(self):
		login_success = self.client.login(username=self.username, password=self.password)
		self.assertTrue(login_success)
		resp = self.client.get("/fs2020/aircraft/add/")
		self.assertEqual(resp.status_code, 200)

	def test_login_view_works(self):
		# use the login URL provided by django.contrib.auth at /core_app/login/
		resp = self.client.post("/core_app/login/", {"username": self.username, "password": self.password}, follow=True)
		# after successful login should be authenticated
		if resp.context:
			user = resp.context.get('user')
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
			'username': 'testuser2',
			'first_name': 'Test',
			'last_name': 'User',
			'email': 'test@example.com',
			'password1': 'ComplexPass123!',
			'password2': 'ComplexPass123!',
		}
		resp = self.client.post("/core_app/signup/", data, follow=True)
		self.assertTrue(User.objects.filter(username='testuser2').exists())
	
	def test_signup_creates_person_with_consent(self):
		"""Test that signup creates a Person record when phone and consent are provided."""
		from prayer.models import Person
		data = {
			'username': 'testuser3',
			'first_name': 'Test',
			'last_name': 'User',
			'email': 'test3@example.com',
			'phone_number': '+12345678900',
			'sms_consent': True,
			'password1': 'ComplexPass123!',
			'password2': 'ComplexPass123!',
		}
		resp = self.client.post("/core_app/signup/", data, follow=True)
		self.assertTrue(User.objects.filter(username='testuser3').exists())
		person = Person.objects.filter(phone_number='+12345678900').first()
		self.assertIsNotNone(person)
		self.assertTrue(person.sms_consent)
		self.assertIsNotNone(person.sms_consent_date)

