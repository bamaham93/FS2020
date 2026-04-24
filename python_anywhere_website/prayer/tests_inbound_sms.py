from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from prayer.models import InboundSmsMessage, Person
from prayer.services import InboundSmsPayload, handle_inbound_sms


class InboundSmsServiceTests(TestCase):
    def test_handle_inbound_sms_creates_message_and_matches_person_by_phone(self):
        person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="(555) 222-3333",
        )
        payload = InboundSmsPayload(
            provider="twilio",
            provider_message_id="SM123",
            from_number="+1 555-222-3333",
            to_number="+18005550100",
            body="Hello there",
        )

        message = handle_inbound_sms(payload)

        self.assertEqual(message.provider_message_id, "SM123")
        self.assertEqual(message.person, person)
        self.assertEqual(InboundSmsMessage.objects.count(), 1)

    def test_handle_inbound_sms_is_idempotent_for_retries(self):
        payload = InboundSmsPayload(
            provider="twilio",
            provider_message_id="SM_RETRY",
            from_number="+15551112222",
            to_number="+18005550100",
            body="Please call me",
        )

        first = handle_inbound_sms(payload)
        second = handle_inbound_sms(payload)

        self.assertEqual(first.id, second.id)
        self.assertEqual(InboundSmsMessage.objects.count(), 1)


class TwilioWebhookTests(TestCase):
    def test_webhook_rejects_invalid_signature(self):
        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "MessageSid": "SM401",
                "From": "+15550001111",
                "To": "+18005550100",
                "Body": "Bad signature",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(InboundSmsMessage.objects.count(), 0)

    @override_settings(TWILIO_AUTH_TOKEN="test-token")
    @patch("prayer.views.RequestValidator.validate", return_value=True)
    def test_webhook_accepts_valid_signature_and_persists_message(self, _validator):
        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "MessageSid": "SM200",
                "From": "+15550001111",
                "To": "+18005550100",
                "Body": "Need prayer",
            },
            HTTP_X_TWILIO_SIGNATURE="sig",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InboundSmsMessage.objects.count(), 1)
        saved = InboundSmsMessage.objects.get(provider_message_id="SM200")
        self.assertEqual(saved.body, "Need prayer")

    @override_settings(TWILIO_AUTH_TOKEN="test-token")
    @patch("prayer.views.RequestValidator.validate")
    def test_webhook_accepts_valid_signature_when_https_fallback_matches(
        self, validator_mock
    ):
        def validate_side_effect(url, _post_data, _signature):
            return url.startswith("https://")

        validator_mock.side_effect = validate_side_effect

        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "MessageSid": "SM201",
                "From": "+15550001111",
                "To": "+18005550100",
                "Body": "Proxy mismatch",
            },
            HTTP_HOST="example.com",
            HTTP_X_TWILIO_SIGNATURE="sig",
            wsgi_url_scheme="http",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InboundSmsMessage.objects.count(), 1)
        self.assertEqual(validator_mock.call_count, 2)

    @override_settings(TWILIO_AUTH_TOKEN="test-token")
    @patch("prayer.views.RequestValidator.validate", return_value=True)
    def test_webhook_returns_400_when_required_fields_missing(self, _validator):
        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "From": "+15550001111",
                "Body": "Missing MessageSid and To",
            },
            HTTP_X_TWILIO_SIGNATURE="sig",
        )

        self.assertEqual(response.status_code, 400)


class InboundMessagesViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="pw", is_staff=True
        )
        self.client.login(username="staff", password="pw")

    def test_inbound_messages_view_shows_unread_and_unassigned(self):
        InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_UNASSIGNED",
            from_number="+15557770000",
            to_number="+18005550100",
            body="Who is this?",
        )

        response = self.client.get(reverse("prayer:inbound_messages"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unread: 1")
        self.assertContains(response, "Unassigned - review needed")
