from django.shortcuts import render
from .models import Race

# Create your views here.
def index(request):
    """
    """
    context = {'races': Race.objects.all().order_by('datetime')}
    return render(request, "douglas/index.html", context)