"""
Functions related to sending text and email messages.
"""

from twilio.rest import Client
import logging
import os

logging.basicConfig(filename="sms_logfile.txt", level=logging.INFO)

os.environ = {
    "TWILIO_ACCOUNT_SID": "AC34cfca8f7148eeb605137f776419d684",
    "TWILIO_AUTH_TOKEN": "36dd32d67536d0084b21f3512dd0bc2e",
}


class Message:
    """
    For sending emails and texts to recipients. If text messaging fails, or if the contact prefers
    email, then an email will be sent.
    """

    def __init__(self, contacts: list, message_body: str, testing_mode: bool):
        """
        Takes a list of contacts represented by a list of tuples from a SQLite3 query.
        """
        self.contacts = contacts
        self.message_body = message_body
        self.testing_mode = testing_mode

        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)

    def send_message(self):
        """
        Handler to route the message to either send_text or _send_email as appropriate.

        Sample contact tuple:
        ('Jacob', 'McGowin', '+12564048322', 'bamaham93@gmail.com', 'True', 'True', 'True')
        """
        # self._send_text(to_number=self.contact[2], message_body=self.message_body)
        # if type(self.contacts[0]) == type(tuple):
        if 1 == 1:
            for contact in self.contacts:
                print(contact)
                self.first_name = contact[0]
                self.last_name = contact[1]
                self.phone_number = contact[2]
                self.email_address = contact[3]
                self.is_member = contact[4]
                self.is_prayer_chain = contact[5]
                self.prefer_text = contact[6]
                self.message_body = self.message_body

                self._send_text()

        # For/each loop over list of contacts
        # dot format on message string to personalize.
        # if prefer_text
        # Try send text
        # Except send email
        # else
        # try/except send email

    def _send_email(self):
        """
        Send an email via SMTP.
        """
        raise NotImplemented("This portion under development.")

    def _send_text(self):
        """
        Send a text message via twilio.
        """
        if not self.testing_mode:
            print(f"Testing Mode OFF")
            try:
                message = self.client.messages.create(
                    body=f"{self.message_body}",
                    from_="+16412126207",
                    to=f"{self.phone_number}",
                )
                # Add logging?
            except:
                # Add logging
                pass
        else:
            print(f"Test Mode ON. Message: {self.message_body}")


if __name__ == "__main__":

    peoples = [
        (
            "Andrew",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "False",
            "True",
            "True",
        ),
        (
            "James",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "True",
            "False",
            "True",
        ),
        (
            "Karen",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "False",
            "False",
            "True",
        ),
        (
            "Hudson",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "True",
            "True",
            "False",
        ),
        (
            "Elisha",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "False",
            "True",
            "False",
        ),
        (
            "Alaina",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "True",
            "False",
            "True",
        ),
        (
            "Juliette",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "False",
            "False",
            "False",
        ),
        (
            "Jacob",
            "McGowin",
            "+12564048322",
            "bamaham93@gmail.com",
            "True",
            "True",
            "True",
        ),
    ]


message_string = r"Hello {first_name}, how are you today?"
# mess = Message(jacob, message_string, testing_mode=False)
mess = Message(contacts=peoples, message_body=message_string, testing_mode=True)
mess.send_message()