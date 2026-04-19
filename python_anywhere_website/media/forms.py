from django import forms
from media.models import Media

"""
"""


class AddMediaForm(forms.ModelForm):
    class Meta:
        """ """

        model = Media
        exclude = []


class BarcodeForm(forms.Form):
    CODE_CHOICES = (
        ("upc", "UPC"),
        ("isbn", "ISBN"),
    )

    code_type = forms.ChoiceField(choices=CODE_CHOICES, initial="upc")
    barcode = forms.CharField(max_length=100, help_text="Enter barcode (UPC or ISBN)")
