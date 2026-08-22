from django.test import TestCase
from django.urls import reverse

from .forms import O2CalculatorForm
from .views import o2_calc


class O2FormTests(TestCase):
    def test_form_valid_and_invalid(self):
        form = O2CalculatorForm(data={"t1": 70, "t2": 100, "p1": 2000})
        self.assertTrue(form.is_valid())

        form_invalid = O2CalculatorForm(data={"t1": 70, "t2": 100, "p1": -5})
        self.assertFalse(form_invalid.is_valid())


class O2ViewTests(TestCase):
    def test_get_shows_form(self):
        resp = self.client.get(reverse("fs2020:o2_calculator"))
        self.assertEqual(resp.status_code, 200)
        # Ensure the view provides the form in the context
        self.assertIn("form", resp.context)
        self.assertIsInstance(resp.context["form"], O2CalculatorForm)

    def test_post_returns_result(self):
        t1 = 70
        t2 = 100
        p1 = 2000
        expected = o2_calc(t1, t2, p1)

        resp = self.client.post(
            reverse("fs2020:o2_calculator"), data={"t1": t1, "t2": t2, "p1": p1}
        )
        self.assertEqual(resp.status_code, 200)
        # Check that the result is passed in the template context
        self.assertIn("result", resp.context)
        self.assertEqual(resp.context["result"]["p2"], expected)
