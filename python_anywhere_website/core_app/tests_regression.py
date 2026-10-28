from django.test import TestCase
from django.urls import reverse


class RegressionTests(TestCase):
    def test_core_index_renders_without_racing_namespace(self):
        """Ensure the core index page renders even when 'racing' namespace is not registered."""
        resp = self.client.get(reverse("core_app:index"))
        self.assertEqual(resp.status_code, 200)

    def test_start_here_page_renders_primary_sections(self):
        resp = self.client.get(reverse("start_here"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Aviation")
        self.assertContains(resp, "Photography")
        self.assertContains(resp, "Tools")
