"""
Functions related to sending text messages.
"""

import logging
from typing import Dict, Set, Tuple

from prayer.models import Person
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

try:
    from credentials.twilio import (
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
    )
except ModuleNotFoundError:
    from credentials.mock_faa_twilio import (
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
    )

logger = logging.getLogger(__name__)


def _mask_phone(phone: str) -> str:
    """Return a masked phone number showing only the last 4 digits."""
    if phone and len(phone) > 4:
        return f"***{phone[-4:]}"
    return "***"


class SMSMessage:
    """
    Sends SMS messages to a set of Person recipients via Twilio.
    Callers receive a per-contact result dict so they can persist send logs.
    """

    def __init__(self, body: str, contacts: Set[Person], testing=False) -> None:
        """
        body: The text of the message to send.
        contacts: A set of Person model instances. Using a set guarantees each
                  person receives at most one message even if they belong to
                  multiple groups.
        testing: When True, prints the message body instead of actually sending.
        """
        self.body = body
        self.contacts = contacts
        self.testing = testing

        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        self.client = Client(account_sid, auth_token)

    def send(self) -> Dict[Person, Tuple[bool, str]]:
        """
        Send message to all contacts.

        Returns a dict mapping each Person to a (success, error_message) tuple
        so the caller can persist SMSLog records.
        """
        results: Dict[Person, Tuple[bool, str]] = {}
        for contact in self.contacts:
            phone_number = contact.phone_number
            if self.testing:
                logger.info(
                    "TEST send to %s %s (%s): %s",
                    contact.first_name,
                    contact.last_name,
                    _mask_phone(phone_number),
                    self.body,
                )
                results[contact] = (True, "")
            else:
                success, error = self._send(
                    message_body=self.body, phone_number=phone_number
                )
                results[contact] = (success, error)
        return results

    def _send(self, message_body: str, phone_number: str) -> Tuple[bool, str]:
        """
        Send a single message to one phone number.

        Returns a (success, error_message) tuple.
        """
        try:
            self.client.messages.create(
                body=str(message_body),
                from_=TWILIO_PHONE_NUMBER,
                to=str(phone_number),
            )
            logger.info("Message to %s sent successfully.", _mask_phone(phone_number))
            return True, ""
        except TwilioRestException as e:
            logger.warning(
                "Message to %s failed to send. %s", _mask_phone(phone_number), e
            )
            return False, str(e)
