from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from prayer.models import InboundSmsMessage, Person
from prayer.services import (
    InboundSmsPayload,
    _get_prayer_admin_persons,
    _notify_admins,
    handle_inbound_sms,
)


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

    @override_settings(TWILIO_AUTH_TOKEN="test-token", ALLOWED_HOSTS=["example.com"])
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

    def _create_inbound_message(self, person=None, processed=False):
        return InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id=f"SM_{InboundSmsMessage.objects.count()}",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
            person=person,
            processed=processed,
        )

    def _create_group_user(self, username="prayer_admin"):
        group = Group.objects.create(name="Prayer Admins")
        user = User.objects.create_user(username=username, password="pw")
        user.groups.add(group)
        return user

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

    def test_inbound_messages_view_shows_sender_and_body(self):
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15557770001",
        )
        InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_ASSIGNED",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
            person=sender,
        )

        response = self.client.get(reverse("prayer:inbound_messages"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Linked to Jane Doe")
        self.assertContains(response, "Please pray for us.")

    def test_inbound_sms_string_includes_sender_and_body(self):
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15557770001",
        )
        message = InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_STR",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
            person=sender,
        )

        self.assertEqual(
            str(message),
            "You have a message from Jane Doe: Please pray for us.",
        )

    def test_inbound_sms_string_falls_back_to_phone_number(self):
        message = InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_STR_PHONE",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
        )

        self.assertEqual(
            str(message),
            "You have a message from +15557770001: Please pray for us.",
        )

    def test_staff_sees_inbound_sms_notification_on_prayer_pages(self):
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15557770001",
        )
        InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_ALERT",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
            person=sender,
        )

        response = self.client.get(reverse("prayer:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 unread inbound SMS")
        self.assertContains(
            response, "You have a message from Jane Doe: Please pray for us."
        )

    def test_prayer_admins_group_member_sees_inbound_sms_notification(self):
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15557770001",
        )
        self._create_inbound_message(person=sender)
        self.client.logout()
        self._create_group_user()
        self.client.login(username="prayer_admin", password="pw")

        response = self.client.get(reverse("prayer:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 unread inbound SMS")
        self.assertContains(
            response, "You have a message from Jane Doe: Please pray for us."
        )

    def test_regular_member_does_not_see_inbound_sms_notification(self):
        InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_HIDDEN",
            from_number="+15557770001",
            to_number="+18005550100",
            body="Please pray for us.",
        )
        self.client.logout()
        User.objects.create_user(username="member", password="pw")
        self.client.login(username="member", password="pw")

        response = self.client.get(reverse("prayer:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "unread inbound SMS")
        self.assertNotContains(response, "Please pray for us.")

    def test_processed_messages_do_not_show_in_notification(self):
        self._create_inbound_message(processed=True)

        response = self.client.get(reverse("prayer:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "unread inbound SMS")
        self.assertNotContains(response, "Please pray for us.")

    def test_prayer_admins_group_member_can_view_inbound_messages_page(self):
        self._create_inbound_message()
        self.client.logout()
        self._create_group_user()
        self.client.login(username="prayer_admin", password="pw")

        response = self.client.get(reverse("prayer:inbound_messages"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please pray for us.")

    def test_regular_member_cannot_view_inbound_messages_page(self):
        self._create_inbound_message()
        self.client.logout()
        User.objects.create_user(username="member", password="pw")
        self.client.login(username="member", password="pw")

        response = self.client.get(reverse("prayer:inbound_messages"))

        self.assertEqual(response.status_code, 302)


class AdminNotificationTests(TestCase):
    """Tests for the _notify_admins / admin-notification path in handle_inbound_sms."""

    ADMIN_GROUP = "Prayer Admin"

    def setUp(self):
        self.group, _ = Group.objects.get_or_create(name=self.ADMIN_GROUP)

    def _make_admin_user(self, username, email, phone_number):
        """Create a User in the Prayer Admin group with a matching Person record."""
        user = User.objects.create_user(username=username, email=email, password="pw")
        user.groups.add(self.group)
        person = Person.objects.create(
            first_name=user.first_name or username,
            last_name=user.last_name or "Admin",
            email=email,
            phone_number=phone_number,
        )
        return user, person

    def _make_message(self, person=None, from_number="+15550001111"):
        return InboundSmsMessage.objects.create(
            provider="twilio",
            provider_message_id="SM_NOTIFY_TEST",
            from_number=from_number,
            to_number="+18005550100",
            body="Hello",
            person=person,
        )

    def test_get_prayer_admin_persons_returns_persons_for_group_members(self):
        """_get_prayer_admin_persons returns Person records matched by email."""
        _, person = self._make_admin_user(
            "admin1", "admin1@example.com", "+15559990000"
        )
        results = _get_prayer_admin_persons()
        self.assertIn(person, results)

    def test_get_prayer_admin_persons_excludes_non_members(self):
        """Person records whose email is not in the group are excluded."""
        Person.objects.create(
            first_name="Not",
            last_name="Admin",
            email="notadmin@example.com",
            phone_number="+15558880000",
        )
        results = _get_prayer_admin_persons()
        self.assertEqual(results, [])

    def test_get_prayer_admin_persons_returns_empty_when_group_missing(self):
        """Returns empty list gracefully when the Prayer Admin group doesn't exist."""
        Group.objects.filter(name=self.ADMIN_GROUP).delete()
        results = _get_prayer_admin_persons()
        self.assertEqual(results, [])

    def test_get_prayer_admin_persons_skips_members_without_person_record(self):
        """Group members with no matching Person (by email) are silently skipped."""
        user = User.objects.create_user(
            username="noperson", email="noperson@example.com", password="pw"
        )
        user.groups.add(self.group)
        results = _get_prayer_admin_persons()
        self.assertEqual(results, [])

    def test_get_prayer_admin_persons_skips_persons_without_phone(self):
        """Person records with no phone number are excluded."""
        user = User.objects.create_user(
            username="nophone", email="nophone@example.com", password="pw"
        )
        user.groups.add(self.group)
        Person.objects.create(
            first_name="No",
            last_name="Phone",
            email="nophone@example.com",
            phone_number=None,
        )
        results = _get_prayer_admin_persons()
        self.assertEqual(results, [])

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_sends_sms_to_prayer_admin_group_members(
        self, mock_client_cls
    ):
        """_notify_admins sends one SMS per Prayer Admin group member with a phone."""
        _, admin_person = self._make_admin_user(
            "alice", "alice@example.com", "+15559990001"
        )
        non_admin = Person.objects.create(
            first_name="Bob",
            last_name="Regular",
            email="bob@example.com",
            phone_number="+15558880001",
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
        self.assertEqual(call_kwargs["to"], admin_person.phone_number)
        self.assertNotEqual(call_kwargs["to"], non_admin.phone_number)

    @patch("prayer.services.TwilioClient")
    def test_notify_admins_uses_person_name_when_matched(self, mock_client_cls):
        """Notification body uses sender's name when a Person is matched."""
        sender = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="+15551112222",
        )
        self._make_admin_user("admin2", "admin2@example.com", "+15559990002")

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
        """Notification body falls back to the raw phone number when no Person matched."""
        self._make_admin_user("admin3", "admin3@example.com", "+15559990003")

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
        """No SMS sent when the Prayer Admin group has no eligible members."""
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
