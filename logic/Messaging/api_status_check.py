"""
"""

import json

import requests


class APIStatus:

    def __init__(self):
        """
        """

    def get_api_status_from_twilio(self):
        """
        """
        list_of_components_desired = [
            "name",
            "sms",
            "sms delivery notifications & status callbacks",
            "sms long code, north america",
            "sms toll-free, north america",
            "rest api",
        ]

        data = json.loads(requests.get("https://status.twilio.com/api/v2/components.json"))

        other_than_operational_list = []
        data_list = []

        # Maybe combine these two for optimisation later?
        [data_list.append(x) for x in data['components'] if x["name"].lower() in list_of_components_desired]
        [other_than_operational_list.append(x) for x in data_list if x["status"] != "operational"]

        return other_than_operational_list
