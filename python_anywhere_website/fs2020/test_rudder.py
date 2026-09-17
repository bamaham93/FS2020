from django.test import TestCase
from django.urls import reverse

from .forms import RudderCalculatorForm
from .views import sas_solver


class RudderFormTests(TestCase):
    def test_form_valid_and_invalid(self):
        form = RudderCalculatorForm(data={"rudder_chord": 12, "travel_deg": 15})
        self.assertTrue(form.is_valid())

        form_invalid = RudderCalculatorForm(data={"rudder_chord": -1, "travel_deg": 15})
        self.assertFalse(form_invalid.is_valid())


class RudderViewTests(TestCase):
    def test_get_shows_form(self):
        resp = self.client.get(reverse("fs2020:rudder_calculator"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("form", resp.context)
        self.assertContains(resp, 'id="rudder-svg"')
        self.assertContains(resp, 'id="deflected-rudder"')
        self.assertContains(resp, 'function updateDiagram()')

    def test_post_returns_result(self):
        chord = 12
        travel = 15
        expected = sas_solver(chord, travel)

        resp = self.client.post(
            reverse("fs2020:rudder_calculator"),
            data={"rudder_chord": chord, "travel_deg": travel},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("result", resp.context)
        self.assertEqual(resp.context["result"]["travel_in"], expected)
