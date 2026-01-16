from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """
    Extended signup form that includes fields for A2P-compliant SMS messaging.
    """

    first_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Required."
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Required."
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Enter a valid email address."
    )
    phone_number = forms.CharField(
        max_length=50,
        required=False,
        help_text="Optional. Enter your phone number if you wish to receive SMS notifications."
    )
    sms_consent = forms.BooleanField(
        required=False,
        label="I consent to receive SMS text messages",
        help_text=(
            "By checking this box, you agree to receive text messages at the phone number provided. "
            "Message and data rates may apply. You can opt out at any time by replying STOP."
        )
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'phone_number',
            'sms_consent',
        )
