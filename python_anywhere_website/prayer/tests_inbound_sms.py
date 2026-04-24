from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from prayer.models import InboundSmsMessage, Person
from prayer.services import InboundSmsPayload, _notify_admins, handle_inbound_sms


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
    @patch("prayer.views.RequestValidator.validate")
    def test_webhook_accepts_valid_signature_with_forwarded_host_and_proto(
        self, validator_mock
    ):
        expected_url = "https://www.jacob-mcgowin.us/api/webhooks/twilio/sms/"

        def validate_side_effect(url, _post_data, _signature):
            return url == expected_url

        validator_mock.side_effect = validate_side_effect

        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "MessageSid": "SM202",
                "From": "+15550001111",
                "To": "+18005550100",
                "Body": "Forwarded host/proto",
            },
            HTTP_HOST="username.pythonanywhere.com",
            HTTP_X_FORWARDED_HOST="www.jacob-mcgowin.us",
            HTTP_X_FORWARDED_PROTO="http,https",
            HTTP_X_TWILIO_SIGNATURE="sig",
            wsgi_url_scheme="http",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InboundSmsMessage.objects.count(), 1)
        validated_urls = [call.args[0] for call in validator_mock.call_args_list]
        self.assertIn(expected_url, validated_urls)

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

    @patch.dict("os.environ", {"TWILIO_AUTH_TOKEN": "env-token"}, clear=False)
    @patch("prayer.views.RequestValidator")
    def test_webhook_uses_env_twilio_token_when_setting_missing(
        self, request_validator_cls
    ):
        request_validator = Mock()
        request_validator.validate.return_value = True
        request_validator_cls.return_value = request_validator

        response = self.client.post(
            "/api/webhooks/twilio/sms/",
            {
                "MessageSid": "SM203",
                "From": "+15550001111",
                "To": "+18005550100",
                "Body": "Env token fallback",
            },
            HTTP_X_TWILIO_SIGNATURE="sig",
        )

        self.assertEqual(response.status_code, 200)
        request_validator_cls.assert_called_once_with("env-token")


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


class AdminNotificationTests(TestCase):
    """Tests for the _notify_admins / admin-notification path in handle_inbound_sms."""

    def _make_message(self, person=None, from_number="+15550001111"):
        return InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_NOTIFY_TEST",
            from_number=from_number,
            to_number="+18005550100",
            body="Hello",
            person=person,
        )

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_sends_sms_to_admin_persons(self, mock_client_cls):
        """_notify_admins sends one SMS per admin with a phone number."""
        admin = Person.objects.create(
            first_name="Alice",
            last_name="Admin",
            phone_number="+15559990000",
            is_admin=True,
        )
        non_admin = Person.objects.create(
            first_name="Bob",
            last_name="Regular",
            phone_number="+15558880000",
            is_admin=False,
        )

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        msg = self._make_message()
        with patch("prayer.services._TWILIO_AVAILABLE", True), patch(
            "prayer.services.TWILIO_ACCOUNT_SID", "ACtest"
        ), patch("prayer.services.TWILIO_AUTH_TOKEN", "tok"), patch(
            "prayer.services.TWILIO_PHONE_NUMBER", "+18001234567"
        ):
            _notify_admins(msg)

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["to"], admin.phone_number)
        self.assertNotEqual(call_kwargs["to"], non_admin.phone_number)

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_uses_person_name_when_matched(self, mock_client_cls):
        """Notification body uses sender's name when a Person is matched."""
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15551112222",
        )
        Person.objects.create(
            first_name="Admin",
            last_name="Person",
            phone_number="+15559990001",
            is_admin=True,
        )

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        msg = self._make_message(person=sender)
        with patch("prayer.services._TWILIO_AVAILABLE", True), patch(
            "prayer.services.TWILIO_ACCOUNT_SID", "ACtest"
        ), patch("prayer.services.TWILIO_AUTH_TOKEN", "tok"), patch(
            "prayer.services.TWILIO_PHONE_NUMBER", "+18001234567"
        ):
            _notify_admins(msg)

        body = mock_client.messages.create.call_args.kwargs["body"]
        self.assertIn("Jane Doe", body)

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_uses_phone_number_when_no_person_match(
        self, mock_client_cls
    ):
        """Notification body uses the raw phone number when no Person is matched."""
        Person.objects.create(
            first_name="Admin",
            last_name="Person",
            phone_number="+15559990002",
            is_admin=True,
        )

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        msg = self._make_message(from_number="+15554440000")
        with patch("prayer.services._TWILIO_AVAILABLE", True), patch(
            "prayer.services.TWILIO_ACCOUNT_SID", "ACtest"
        ), patch("prayer.services.TWILIO_AUTH_TOKEN", "tok"), patch(
            "prayer.services.TWILIO_PHONE_NUMBER", "+18001234567"
        ):
            _notify_admins(msg)

        body = mock_client.messages.create.call_args.kwargs["body"]
        self.assertIn("+15554440000", body)

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_skips_when_no_admins(self, mock_client_cls):
        """No SMS sent when there are no admin persons."""
        msg = self._make_message()
        _notify_admins(msg)
        mock_client_cls.assert_not_called()

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_skips_admin_without_phone_number(self, mock_client_cls):
        """Admins with no phone number are skipped."""
        Person.objects.create(
            first_name="No",
            last_name="Phone",
            phone_number=None,
            is_admin=True,
        )

        msg = self._make_message()
        _notify_admins(msg)
        mock_client_cls.assert_not_called()

    @patch("prayer.services._notify_admins")
    def test_handle_inbound_sms_notifies_admins_on_new_message(self, mock_notify):
        """handle_inbound_sms calls _notify_admins exactly once for a new message."""
        payload = InboundSmsPayload(
            provider="twilio",
            provider_message_id="SM_HANDLE_NEW",
            from_number="+15550005555",
            to_number="+18005550100",
            body="New message",
        )

        handle_inbound_sms(payload)
        mock_notify.assert_called_once()

    @patch("prayer.services._notify_admins")
    def test_handle_inbound_sms_does_not_notify_on_duplicate(self, mock_notify):
        """handle_inbound_sms does NOT call _notify_admins for duplicate messages."""
        payload = InboundSmsPayload(
            provider="twilio",
            provider_message_id="SM_HANDLE_DUP",
            from_number="+15550005556",
            to_number="+18005550100",
            body="Duplicate",
        )

        handle_inbound_sms(payload)
        handle_inbound_sms(payload)
        mock_notify.assert_called_once()
