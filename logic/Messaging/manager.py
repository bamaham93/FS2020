"""
Receives the messages from Django and manager the process of sending the messages.
"""

from typing import Set
from prayer.models import People
from api_status_check import APIStatus


class MessageManager:
    """
    """

    def __init__(self):
        """
        """

    def _get_permissions(self):
        """
        Gets permissions from the database for each contact so that messages can be routed appropriately.
        """

    def _check_twilio_sms_api(self):
        """
        Gets the status of the Twilio SMS api so that the message router can reroute messages as needed.
        """

    def _check_sendgrid_api(self):
        """
        Gets the status of the Twilio SendGrid api so that the message router can reroute messages as needed.
        """
        status = APIStatus()
        status_list = status.get_api_status_from_twilio()
        self.status_list = status_list

    def _send_sms(self, contact_set: Set[People]):
        """
        """

    def _send_email(self, contact_set: Set[People]):
        """
        """
        for person in contact_set:
            pass
