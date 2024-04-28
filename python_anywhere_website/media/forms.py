from django import forms
from media.models import Media

"""
"""

class AddMediaForm(forms.ModelForm):
    class Meta:
        """
        """
        model = Media
        exclude = []
