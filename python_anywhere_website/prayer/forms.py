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


class PublicSignupForm(forms.ModelForm):
    """Form for public SMS signup without requiring login."""

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
        ]
        help_texts = {
            "phone_number": "We'll send prayer updates to this number. Standard messaging rates may apply.",
            "email": "Optional - for account recovery purposes only.",
        }
        labels = {
            "phone_number": "Mobile Phone Number",
            "email": "Email Address (Optional)",
        }


class PermissionsForm(forms.ModelForm):
    """ """

    class Meta:
        model = Permissions
        fields = [
            "may_send_emails",
            "may_send_sms",
        ]
