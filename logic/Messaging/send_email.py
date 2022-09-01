"""
Sends email messages using SendGrid's Python Library
https://github.com/sendgrid/sendgrid-python
"""

import logging
import os

from datetime.datetime import now
from dotenv import load_env
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_env()


def _send_email(to_address: str, subject: str, body: str):
    """
    Note that body can be HTML stlyed.
    """
    message = Mail(
        from_email='info@jacob-mcgowin.us',
        to_emails=f'{to_address}',
        subject=f'{subject}',
        html_content=f'{body}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        # print(e.message)
        logging.warning(f"{now} {e}")
