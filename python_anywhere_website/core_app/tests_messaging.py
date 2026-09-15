from pathlib import Path
import sys
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import SimpleTestCase

LOGIC_ROOT = Path(settings.BASE_DIR).parent
if str(LOGIC_ROOT) not in sys.path:
    sys.path.insert(0, str(LOGIC_ROOT))

from logic.Messaging.api_status_check import APIStatus
from logic.Messaging.sms import SMSMessage, clean_for_sms


class APIStatusTests(SimpleTestCase):
    def test_get_api_status_from_twilio_filters_non_operational_components(self):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "components": [
                {"name": "SMS", "status": "operational"},
                {"name": "REST API", "status": "major_outage"},
                {"name": "Email", "status": "operational"},
                {
                    "name": "SMS Long Code, North America",
                    "status": "degraded_performance",
                },
            ]
        }

        with patch(
            "logic.Messaging.api_status_check.requests.get", return_value=mock_response
        ) as mock_get:
            status = APIStatus()
            result = status.get_api_status_from_twilio()

        mock_get.assert_called_once_with(
            "https://status.twilio.com/api/v2/components.json"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            result,
            [
                {"name": "REST API", "status": "major_outage"},
                {
                    "name": "SMS Long Code, North America",
                    "status": "degraded_performance",
                },
            ],
        )


class SmsEncodingTests(SimpleTestCase):
    def test_clean_for_sms_removes_emoji_and_collapses_whitespace(self):
        self.assertEqual(
            clean_for_sms("  Don’t forget 🙏  to pray 👍\t\t  "),
            "Don’t forget to pray",
        )

    @patch("logic.Messaging.sms.Client")
    def test_send_uses_cleaned_body_and_smart_encoding(self, mock_client_class):
        mock_client = mock_client_class.return_value
        sms = SMSMessage(body="Don’t forget 🙏", contacts=set())

        success, error = sms._send(
            message_body=sms.body, phone_number="+15551234567"
        )

        self.assertTrue(success)
        self.assertEqual(error, "")
        mock_client.messages.create.assert_called_once_with(
            body="Don’t forget",
            from_="",
            to="+15551234567",
            smart_encoded=True,
        )
