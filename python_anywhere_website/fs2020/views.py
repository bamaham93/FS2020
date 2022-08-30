from django.shortcuts import render
from .models import Aircraft, Flight
from .faa.notams import NOTAMS

# Create your views here.
def index(request):
    """
    FS2020 app home page.
    """
    context = {"title": "FS2020 Home"}
    context["aircraft"] = Aircraft.objects.all()
    return render(request, "fs2020/index.html", context)


def flights(request, n_number):
    """ """
    context = {}
    context["flights"] = Flight.objects.filter(n_num__exact=n_number)
    return render(request, "fs2020/flights.html", context)


def notams(request):
    """
    Search NOTAMS by airport.
    """
    notams_ = NOTAMS()
    context = {"notams": notams_.get_airport_notams()}
    return render(request, "fs2020/notams.html", context)
