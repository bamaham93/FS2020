from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone
from .forms import SignUpForm
from prayer.models import Person

# Create your views here.
def index(request):
    """
    Website home page.
    """
    context = {}
    return render(request, "core_app/index.html", context)


def profile(request):
    """ """
    return render(request, "Hello.")


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "core_app/signup.html"

    def form_valid(self, form):
        # Save the user
        response = super().form_valid(form)
        
        # Create a Person record if phone number is provided
        phone_number = form.cleaned_data.get('phone_number')
        sms_consent = form.cleaned_data.get('sms_consent')
        
        if phone_number:
            Person.objects.create(
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                phone_number=phone_number,
                email=form.cleaned_data.get('email'),
                sms_consent=sms_consent,
                sms_consent_date=timezone.now() if sms_consent else None
            )
        
        return response
