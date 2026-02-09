from django import forms
from .models import Aircraft

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

class O2CalculatorForm(forms.Form):
    t1 = forms.FloatField(label="Initial temperature (°F)", min_value=-200, max_value=1000)
    t2 = forms.FloatField(label="Final temperature (°F)", min_value=-200, max_value=1000)
    p1 = forms.FloatField(label="Initial pressure (PSI)", min_value=0)

    def clean(self):
        cleaned = super().clean()
        t1 = cleaned.get("t1")
        t2 = cleaned.get("t2")
        p1 = cleaned.get("p1")
        if t1 is None or t2 is None or p1 is None:
            return cleaned
        return cleaned
