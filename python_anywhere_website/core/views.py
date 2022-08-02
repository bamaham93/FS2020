from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# Create your views here.
def index(request):
    """
    Website home page.
    """
    context = {}
    return render(request, "core/index.html", context)


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "core/signup.html"


def login(request):
    """
    """
    context = {}
    return render(request, 'core/login.html', context)


def logout(request):
    """
    """
    context = {}
    return redirect('core:index')