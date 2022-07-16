from django.shortcuts import render
from .models import Race
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    """
    """
    context = {}
    return render(request, 'douglas/index.html', context=context)

def nis_index(request):
    """
    """
    context = {'races': Race.objects.all().filter().order_by('datetime')}
    return render(request, "douglas/nis_index.html", context)

@login_required
def add_race_result(request):
    """
    View to add race results to database.
    """
    context = {}
    return render(request, "douglas/add_results.html", context=context)