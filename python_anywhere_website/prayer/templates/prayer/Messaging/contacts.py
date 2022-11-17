"""
A person to be contacted; Handles the message, addresses them by name or title
as
"""

import logging
import datetime

logging.basicConfig(filename="message_log.txt", level=logging.INFO)


class Contact:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        title: str,
        email_address: str,
        phone_number: str,
        prefer_text: bool,
    ):
        """
        first_name:str;
        last_name:str;
        title:str; Mr., Ms., or Mrs.
        email_address:str; Properly formatted email address.
        phone_number:str; Properly formatted (E.164) phone number.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.email_address = email_address
        self.phone_number = phone_number
        self.prefer_text = prefer_text

    def message_type_handler(self):
        """
        Attempts to send a message via the preferred method. If not able, falls
        back to other method. If successful in sending the message, log message
        and method. If both fail, log the failure.
        """
        if self.prefer_text:
            # Send a text
            try:
                pass
            except:
                pass
            pass
        else:  # Prefer email
            # Send an email
            try:
                pass
            except:
                pass

    def log(self, success: bool, method: str):
        """
        success:bool; Message sent successfully or not.
        method:str; Either sms or email.

        Logs successful, unsuccessful messages for later analysis as needed.
        """

        now = datetime.datetime.now()

        if success:
            logging.INFO(
                f"{now} message sent via {method} to {self.first_name} {self.last_name}."
            )
        else:
            logging.WARNING(
                f"{now} messages sent via {method} to {self.first_name} {self.last_name} failed."
            )
