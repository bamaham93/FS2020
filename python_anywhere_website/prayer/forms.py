from django import forms
from prayer.models import PrayerGroup, Person, PrayerMessage, Permissions


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
            "sms_consent",
        ]


class NewMessageForm(forms.ModelForm):
    """ """

    class Meta:
        model = PrayerMessage
        fields = [
            "name",
            "subject",
            "message",
        ]


class NewPrayerRequestForm(forms.ModelForm):
    """Form used on the public Prayer Requests page to collect requests."""

    class Meta:
        model = PrayerMessage
        fields = [
            "subject",
            "message",
        ]
        labels = {
            "subject": "Subject",
            "message": "Prayer request",
        }


class PermissionsForm(forms.ModelForm):
    """ """

    class Meta:
        model = Permissions
        fields = [
            "may_send_emails",
            "may_send_sms",
        ]
