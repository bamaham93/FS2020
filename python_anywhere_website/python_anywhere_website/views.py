from django.shortcuts import render
# from .models import Aircraft, Flight
from django.shortcuts import redirect

# Create your views here.
def redirect_home(request):
    """
    Redirects to the FS2020 app home page.
    """
    response = redirect('core:index')
    return response