"""
Tests for the logic.Messaging module.

This module tests the API status checking, message management, SMS, and email functionality
with mocked external dependencies to avoid making actual API calls during testing.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

# Add the parent directory to the path so we can import from logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestApiStatusCheck(TestCase):
    """
    Tests for the APIStatus class that checks Twilio API status.
    """

    @patch("logic.Messaging.api_status_check.requests.get")
    def test_get_api_status_all_operational(self, mock_get):
        """
        Test that when all components are operational, empty list is returned.
        """
        from logic.Messaging.api_status_check import APIStatus

        # Mock response data with all operational status
        # The api_status_check.py code calls json.loads() on the response object,
        # so we need to return a string that json.loads can parse
        json_string = """{
            "components": [
                {"name": "SMS", "status": "operational"},
                {"name": "REST API", "status": "operational"},
                {"name": "SMS Delivery Notifications & Status Callbacks", "status": "operational"}
            ]
        }"""
        mock_get.return_value = json_string

        api_status = APIStatus()
        result = api_status.get_api_status_from_twilio()

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            "https://status.twilio.com/api/v2/components.json"
        )

    @patch("logic.Messaging.api_status_check.requests.get")
    def test_get_api_status_with_issues(self, mock_get):
        """
        Test that non-operational components are returned in the list.
        """
        from logic.Messaging.api_status_check import APIStatus

        # Mock response data with one non-operational component
        json_string = """{
            "components": [
                {"name": "SMS", "status": "degraded_performance"},
                {"name": "REST API", "status": "operational"},
                {"name": "SMS Long Code, North America", "status": "operational"}
            ]
        }"""
        mock_get.return_value = json_string

        api_status = APIStatus()
        result = api_status.get_api_status_from_twilio()

        # Should return the non-operational component
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "SMS")
        self.assertEqual(result[0]["status"], "degraded_performance")

    @patch("logic.Messaging.api_status_check.requests.get")
    def test_get_api_status_filters_irrelevant_components(self, mock_get):
        """
        Test that only relevant components are checked for status.
        """
        from logic.Messaging.api_status_check import APIStatus

        # Mock response with both relevant and irrelevant components
        json_string = """{
            "components": [
                {"name": "SMS", "status": "operational"},
                {"name": "Voice", "status": "degraded_performance"},
                {"name": "Programmable Video", "status": "major_outage"}
            ]
        }"""
        mock_get.return_value = json_string

        api_status = APIStatus()
        result = api_status.get_api_status_from_twilio()

        # Voice and Video should be filtered out as they're not in the desired list
        self.assertEqual(result, [])

    @patch("logic.Messaging.api_status_check.requests.get")
    def test_get_api_status_handles_network_error(self, mock_get):
        """
        Test that network errors are handled appropriately.
        """
        from logic.Messaging.api_status_check import APIStatus
        import requests

        # Mock a network error
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        api_status = APIStatus()

        # Should raise the exception (or could be caught and handled in production code)
        with self.assertRaises(requests.exceptions.RequestException):
            api_status.get_api_status_from_twilio()


class TestEmail(TestCase):
    """
    Tests for the email sending functionality using SendGrid.
    """

    @patch("os.environ.get")
    @patch("sendgrid.SendGridAPIClient")
    def test_send_email_success(self, mock_sendgrid_client, mock_env_get):
        """
        Test successful email sending with mocked SendGrid client.
        """
        from logic.Messaging.send_email import _send_email

        # Mock environment variable
        mock_env_get.return_value = "test_api_key"

        # Mock SendGrid client and response
        mock_sg_instance = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.body = "Success"
        mock_response.headers = {}
        mock_sg_instance.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_sg_instance

        # Should not raise any exceptions
        try:
            _send_email(
                to_address="test@example.com",
                subject="Test Subject",
                body="<h1>Test Body</h1>",
            )
            # Verify the SendGrid client was called
            mock_sendgrid_client.assert_called_once_with("test_api_key")
        except Exception as e:
            self.fail(f"_send_email raised an exception: {e}")

    @patch("logging.warning")
    @patch("os.environ.get")
    @patch("sendgrid.SendGridAPIClient")
    def test_send_email_failure(
        self, mock_sendgrid_client, mock_env_get, mock_logging
    ):
        """
        Test that email sending failures are logged appropriately.
        """
        from logic.Messaging.send_email import _send_email

        # Mock environment variable
        mock_env_get.return_value = "test_api_key"

        # Mock SendGrid client to raise an exception
        mock_sg_instance = Mock()
        mock_sg_instance.send.side_effect = Exception("API Error")
        mock_sendgrid_client.return_value = mock_sg_instance

        # Should handle the exception gracefully
        _send_email(
            to_address="test@example.com", subject="Test Subject", body="Test Body"
        )

        # Verify that the error was logged
        self.assertTrue(mock_logging.called)


class TestSms(TestCase):
    """
    Tests for the SMSMessage class using Twilio.
    """

    def setUp(self):
        """
        Set up test fixtures for SMS tests.
        """
        from prayer.models import Person

        # Create mock Person objects
        self.mock_person1 = Mock(spec=Person)
        self.mock_person1.first_name = "John"
        self.mock_person1.last_name = "Doe"
        self.mock_person1.phone_number = "+12345678901"

        self.mock_person2 = Mock(spec=Person)
        self.mock_person2.first_name = "Jane"
        self.mock_person2.last_name = "Smith"
        self.mock_person2.phone_number = "+12345678902"

        self.contacts = {self.mock_person1, self.mock_person2}

    @patch("twilio.rest.Client")
    def test_sms_initialization(self, mock_twilio_client):
        """
        Test that SMSMessage initializes properly with contacts.
        """
        from logic.Messaging.sms import SMSMessage

        message = SMSMessage(
            body="Test message", contacts=self.contacts, testing=True
        )

        self.assertEqual(message.body, "Test message")
        self.assertEqual(message.contacts, self.contacts)
        self.assertTrue(message.testing)
        # Verify Twilio client was initialized
        mock_twilio_client.assert_called_once()

    @patch("twilio.rest.Client")
    def test_sms_send_testing_mode(self, mock_twilio_client):
        """
        Test that in testing mode, messages are printed but not sent.
        """
        from logic.Messaging.sms import SMSMessage

        message = SMSMessage(
            body="Test message", contacts=self.contacts, testing=True
        )

        # In testing mode, should not call _send method
        with patch("builtins.print") as mock_print:
            message.send()
            # Should print the message body for each contact
            self.assertEqual(mock_print.call_count, 2)

    @patch("twilio.rest.Client")
    def test_sms_send_production_mode(self, mock_twilio_client):
        """
        Test that in production mode, messages are sent via Twilio.
        """
        from logic.Messaging.sms import SMSMessage

        # Mock the Twilio client's messages.create method
        mock_client_instance = Mock()
        mock_messages = Mock()
        mock_client_instance.messages = mock_messages
        mock_twilio_client.return_value = mock_client_instance

        message = SMSMessage(
            body="Test message", contacts=self.contacts, testing=False
        )

        message.send()

        # Verify that messages.create was called for each contact
        self.assertEqual(mock_messages.create.call_count, 2)

    @patch("logging.basicConfig")
    @patch("twilio.rest.Client")
    def test_sms_send_handles_twilio_exception(
        self, mock_twilio_client, mock_logging_config
    ):
        """
        Test that Twilio exceptions are handled gracefully and logged.
        """
        from logic.Messaging.sms import SMSMessage
        from twilio.base.exceptions import TwilioRestException

        # Mock the Twilio client to raise an exception
        mock_client_instance = Mock()
        mock_messages = Mock()
        mock_messages.create.side_effect = TwilioRestException(
            status=400, uri="test", msg="Test error", code=400
        )
        mock_client_instance.messages = mock_messages
        mock_twilio_client.return_value = mock_client_instance

        message = SMSMessage(
            body="Test message", contacts=self.contacts, testing=False
        )

        # Should handle the exception without crashing
        try:
            message.send()
        except TwilioRestException:
            self.fail("SMSMessage.send() should handle TwilioRestException gracefully")

    @patch("twilio.rest.Client")
    def test_sms_handles_missing_phone_number(self, mock_twilio_client):
        """
        Test that missing phone numbers are handled gracefully.
        """
        from logic.Messaging.sms import SMSMessage

        # Create a mock person without a phone_number attribute
        mock_person_no_phone = Mock()
        mock_person_no_phone.first_name = "NoPhone"
        mock_person_no_phone.last_name = "Person"
        del mock_person_no_phone.phone_number  # Remove the attribute

        contacts_with_error = {mock_person_no_phone}

        message = SMSMessage(
            body="Test message", contacts=contacts_with_error, testing=True
        )

        # Should handle the missing attribute without crashing
        try:
            with patch("builtins.print"):
                message.send()
        except AttributeError:
            self.fail(
                "SMSMessage.send() should handle missing phone_number gracefully"
            )

    @patch("twilio.rest.Client")
    def test_sms_message_body_formatting(self, mock_twilio_client):
        """
        Test that message body is correctly formatted for each recipient.
        """
        from logic.Messaging.sms import SMSMessage

        test_body = "Hello, this is a test message!"

        message = SMSMessage(body=test_body, contacts=self.contacts, testing=True)

        with patch("builtins.print") as mock_print:
            message.send()
            # Verify the message body was used
            for call in mock_print.call_args_list:
                self.assertEqual(call[0][0], test_body)
