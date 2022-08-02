from django import forms
from prayer.models import PrayerGroup, Person

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

class NewGroupForm(forms.ModelForm):
    """
    """
    class Meta:
        model = PrayerGroup
        fields = ['name', 'short_description', 'long_description', 'people',]


class NewPersonForm(forms.ModelForm):
    """
    """
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'phone_number', 'email',]
