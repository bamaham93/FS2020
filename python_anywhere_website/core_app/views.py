from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.utils.decorators import method_decorator
from django.utils import timezone
from .forms import SignUpForm
from prayer.models import Person


def public_view(view):
    """Mark a view as publicly accessible for LoginRequiredMiddleware setups."""
    view.login_required = False
    return view


# Create your views here.
@public_view
def index(request):
    """
    Website home page.
    """
    context = {}
    return render(request, "core_app/index.html", context)


def profile(request):
    """ """
    return render(request, "Hello.")


@public_view
def privacy_policy(request):
    """
    Display the privacy policy page.
    """
    return render(request, "core_app/privacy_policy.html")


@public_view
def terms_of_service(request):
    """
    Display the terms of service page.
    """
    return render(request, "core_app/terms_of_service.html")


@method_decorator(public_view, name="dispatch")
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "core_app/signup.html"

    def form_valid(self, form):
        # Save the user
        response = super().form_valid(form)

        # Create a Person record if phone number is provided
        phone_number = form.cleaned_data.get("phone_number")
        sms_consent = form.cleaned_data.get("sms_consent")

        if phone_number:
            try:
                Person.objects.create(
                    user=self.object,
                    first_name=form.cleaned_data.get("first_name"),
                    last_name=form.cleaned_data.get("last_name"),
                    phone_number=phone_number,
                    email=form.cleaned_data.get("email"),
                    sms_consent=sms_consent,
                    sms_consent_date=timezone.now() if sms_consent else None,
                )
            except Exception as e:
                # Log the error but don't fail the user creation
                # The user account is already created at this point
                import logging

                logging.error(f"Failed to create Person record during signup: {e}")

        return response
