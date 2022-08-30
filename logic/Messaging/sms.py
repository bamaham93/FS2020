"""
Functions related to sending text messages.
"""

import logging
from typing import Set

from prayer.models import Person
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

try:
    from credentials.twilio import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
except ModuleNotFoundError:
    from credentials.mock_faa_twilio import (
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
         )

logging.basicConfig(filename="sms_logfile.txt", level=logging.INFO)


class SMSMessage:
    """
    For sending emails and texts to recipients. If text messaging fails, or if the contact prefers
    email, then an email will be sent.
    """

    def __init__(self, body: str, contacts: Set[Person], testing=False) -> None:
        """
        """
        self.body = body
        self.contacts = contacts
        self.testing = testing

        # account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        # auth_token = os.environ["TWILIO_AUTH_TOKEN"]

        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        self.client = Client(account_sid, auth_token)


    def send(self) -> None:
        """
        Send message to list of contacts.
        """
        for contact in self.contacts:
            first_name = contact.first_name
            last_name = contact.last_name
            try:
                phone_number = contact.phone_number
            except Exception as e:
                print(e)

            # Formats the message body; uses the f-string syntax to lazily
            # replace those tags with the personal information for that specific
            # person.
            # body = self.body.format(
            #     first_name=first_name,
            #     last_name=last_name)
            body = self.body

            if self.testing:
                print(body)
            else:
                self._send(message_body=body, phone_number=phone_number)

    def _send(self, message_body: str, phone_number: str) -> None:
        """
        Sends each individual message.
        """
        try:
            message = self.client.messages.create(
                body=f"{str(message_body)}",
                from_=TWILIO_PHONE_NUMBER,
                to=f"{str(phone_number)}",
            )
        except TwilioRestException as e:
            logging.WARNING(f"Message to {phone_number} failed to send.{e}")


peoples = [
    (
        "Andrew",
        "McGowin",
        "+12564048322",
    ),
    (
        "James",
        "McGowin",
        "+12564048322",
    ),
    (
        "Karen",
        "McGowin",
        "+12564048322",
    ),
    (
        "Hudson",
        "McGowin",
        "+12564048322",
    ),
    (
        "Elisha",
        "McGowin",
        "+12564048322",
    ),
    (
        "Alaina",
        "McGowin",
        "+12564048322",
    ),
    (
        "Juliette",
        "McGowin",
        "+12564048322",
    ),
    (
        "Jacob",
        "McGowin",
        "+12564048322",
    ),
]

if __name__ == "__main__":
    # text = "Hello {first_name} {last_name}, how are you today?"
    # message = SMSMessage(body=text, contacts=peoples, testing=False)
    # message.send()

    pass
    # result = PrayerGroupQueries.get_group_members(name='CBC Members')
    # print(result)
