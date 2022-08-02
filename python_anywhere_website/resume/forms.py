"""
Forms for the resume app.
"""

from django.forms import ModelForm
from resume.models import Message


class ContactMeForm(ModelForm):
    """ """

    class Meta:
        model = Message
        fields = "__all__"
