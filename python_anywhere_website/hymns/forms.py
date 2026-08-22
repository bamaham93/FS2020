from django import forms

from hymns.models import HymnalEntry, ServicePlan, ServicePlanItem


class ServicePlanForm(forms.ModelForm):
    class Meta:
        model = ServicePlan
        fields = ["title", "service_date", "notes"]
        widgets = {
            "service_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ServicePlanItemForm(forms.ModelForm):
    class Meta:
        model = ServicePlanItem
        fields = ["hymnal_entry", "position", "notes"]

    hymnal_entry = forms.ModelChoiceField(
        queryset=HymnalEntry.objects.none(),
        label="Hymn",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hymnal_entry"].queryset = HymnalEntry.objects.filter(
            is_approved=True
        ).select_related("hymnal")

