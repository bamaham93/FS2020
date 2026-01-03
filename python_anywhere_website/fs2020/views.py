from django.http import JsonResponse
# API endpoint: Return METAR as JSON for a given ICAO code
def metar_api(request):
    icao = request.GET.get('icao', '').strip().upper()
    if not icao:
        return JsonResponse({'error': 'Missing ICAO code'}, status=400)
    data = fetch_metar(icao)
    if not data:
        return JsonResponse({'error': f'No METAR found for {icao}'}, status=404)
    return JsonResponse(data)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Aircraft, Flight
from .faa.notams import NOTAMS
from .forms import AircraftForm
from .metar import fetch_metar
from django.conf import settings

# Create your views here.
def index(request):
    """
    FS2020 app home page.
    """
    context = {"title": "FS2020 Home"}
    aircraft_qs = Aircraft.objects.all()

    # No server-side METAR fetching; handled client-side for speed.

    context["aircraft"] = aircraft_qs
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


@login_required
def aircraft_add(request):
    """Add a new aircraft."""
    if request.method == "POST":
        form = AircraftForm(request.POST)
        if form.is_valid():
            plane = form.save()
            messages.success(request, f"Aircraft {plane.n_num} added.")
            return redirect("fs2020:index")
    else:
        form = AircraftForm()
    return render(request, "fs2020/aircraft_form.html", {"form": form, "title": "Add Aircraft"})


@login_required
def aircraft_edit(request, pk):
    """Edit an existing aircraft."""
    plane = get_object_or_404(Aircraft, pk=pk)
    if request.method == "POST":
        form = AircraftForm(request.POST, instance=plane)
        if form.is_valid():
            plane = form.save()
            messages.success(request, f"Aircraft {plane.n_num} updated.")
            return redirect("fs2020:index")
    else:
        form = AircraftForm(instance=plane)
    return render(request, "fs2020/aircraft_form.html", {"form": form, "title": "Edit Aircraft", "plane": plane})
