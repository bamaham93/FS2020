from django import forms
from prayer.models import PrayerGroup, Person, PrayerMessage, Permissions

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class NewGroupForm(forms.ModelForm):
    """ """

    class Meta:
        model = PrayerGroup
        fields = [
            "name",
            "short_description",
            "long_description",
        ]


class NewPersonForm(forms.ModelForm):
    """ """

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
        ]


class NewMessageForm(forms.ModelForm):
    """
    """
    class Meta:
        model = PrayerMessage
        fields = [
            "name",
            "subject",
            "message",
        ]

class PermissionsForm(forms.ModelForm):
    """
    """
    class Meta:
        model = Permissions
        fields = [
            'may_send_emails',
            'may_send_sms',
        ]