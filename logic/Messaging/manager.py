"""
Receives the messages from Django and manager the process of sending the messages.
"""

from prayer.models import People
from api_status_check import APIStatus
from typing import Set


class MessageManager:
    """ """

    def __init__(self, people_set: Set):
        """ """
        self.people_set = people_set

        self.people_set.map(self._set_flags())

    def _get_permissions(self):
        """
        Gets permissions from the database for each contact so that messages can be routed appropriately.
        """

    def _check_api(self):
        """
        Gets the status of the Twilio SendGrid api so that the message router can reroute messages as needed.
        """
        status = APIStatus()
        status_list = status.get_api_status_from_twilio()
        self.status_list = status_list

    def _send_sms(self, contact_set: Set[People]):
        """ """

    def _send_email(self, contact_set: Set[People]):
        """ """
        for person in self.people_set:
            person

    @staticmethod
    def _set_flags(person):
        """ """
        person.sent_email = False
        person.sent_sms = False
