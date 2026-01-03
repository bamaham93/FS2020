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
