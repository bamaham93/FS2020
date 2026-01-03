from django import forms
from .models import Aircraft


class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = [
            "n_num",
            "make",
            "model",
            "icao_location",
            "status",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
