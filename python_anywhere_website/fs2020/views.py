from django.http import JsonResponse


# API endpoint: Return METAR as JSON for a given ICAO code
def metar_api(request):
    icao = request.GET.get("icao", "").strip().upper()
    if not icao:
        return JsonResponse({"error": "Missing ICAO code"}, status=400)
    data = fetch_metar(icao)
    if not data:
        return JsonResponse({"error": f"No METAR found for {icao}"}, status=404)
    return JsonResponse(data)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Aircraft, Flight
from .faa.notams import NOTAMS
from .forms import AircraftForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Aircraft, Flight
from .faa.notams import NOTAMS
from .forms import AircraftForm, O2CalculatorForm
from .forms import RudderCalculatorForm
from .metar import fetch_metar
from django.conf import settings
import math


# Helper functions ported from the original gist
def convert_f_to_k(f: float) -> float:
    """Convert degrees Fahrenheit to Kelvin."""
    return ((f - 32) / 1.8) + 273.15


def o2_calc(t1, t2, p1):
    """Compute expected pressure P2 given T1, T2 (°F) and P1 (PSI).

    Uses proportional relationship P2 = (T2_K / T1_K) * P1
    """
    t1_abs = convert_f_to_k(t1)
    t2_abs = convert_f_to_k(t2)
    p2 = t2_abs / t1_abs * p1
    return float(format(p2, ".2f"))


def metar_api(request):
    """API endpoint: Return METAR as JSON for a given ICAO code."""
    icao = request.GET.get("icao", "").strip().upper()
    if not icao:
        return JsonResponse({"error": "Missing ICAO code"}, status=400)
    data = fetch_metar(icao)
    if not data:
        return JsonResponse({"error": f"No METAR found for {icao}"}, status=404)
    return JsonResponse(data)


# Create your views here.
def index(request):
    """FS2020 app home page."""
    context = {"title": "FS2020 Home"}
    aircraft_qs = Aircraft.objects.all()
    context["aircraft"] = aircraft_qs
    return render(request, "fs2020/index.html", context)


def flights(request, n_number=None):
    """Display flight history for a specific aircraft or all flights."""
    if n_number:
        flights_qs = Flight.objects.filter(n_num__exact=n_number)
    else:
        flights_qs = Flight.objects.all()
    return render(request, "fs2020/flights.html", {"flights": flights_qs})


def notams(request):
    notams_client = NOTAMS()
    result = notams_client.get_airport_notams()
    context = {}
    if isinstance(result, dict) and result.get("error"):
        status = result.get("status")
        if status == 401:
            message = "NOTAMS are unavailable. The FAA API credentials are invalid or missing."
        else:
            message = "NOTAMS are unavailable right now. Please try again later."
        context["notams_error"] = {
            "message": message,
            "status": status,
        }
    else:
        context["notams_data"] = result
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
    return render(
        request, "fs2020/aircraft_form.html", {"form": form, "title": "Add Aircraft"}
    )


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
    return render(
        request,
        "fs2020/aircraft_form.html",
        {"form": form, "title": "Edit Aircraft", "plane": plane},
    )


def o2_calculator(request):
    """Web form for the O2/bottle-pressure calculator ported from the gist."""
    result = None
    if request.method == "POST":
        form = O2CalculatorForm(request.POST)
        if form.is_valid():
            t1 = form.cleaned_data["t1"]
            t2 = form.cleaned_data["t2"]
            p1 = form.cleaned_data["p1"]
            p2 = o2_calc(t1, t2, p1)
            result = {"p2": p2}
    else:
        form = O2CalculatorForm()
    return render(
        request, "fs2020/o2_calculator.html", {"form": form, "result": result}
    )


def sas_solver(r_length, travel_req):
    """Solve SAS triangle for linear travel B given rudder chord and required angle.

    r_length: Decimal or float, chord in inches
    travel_req: Decimal or float, degrees
    Returns: Decimal linear travel (same units as r_length)
    """
    from decimal import Decimal

    A = Decimal(r_length)
    C = Decimal(r_length)
    a = Decimal(travel_req)

    # convert to radians for math.cos (use float for trig)
    a_rad = float(a) * (math.pi / 180.0)
    a_cos = Decimal(math.cos(a_rad))

    e_1 = A * A + C * C
    e_2 = (2 * A) * C * a_cos
    e_3 = e_1 - e_2
    # e_3 should be non-negative; guard small negative due to rounding
    if e_3 < 0:
        e_3 = Decimal(0)
    e_4 = Decimal(math.sqrt(float(e_3)))
    B = e_4
    return B.quantize(Decimal("0.01"))


def rudder_calculator(request):
    """Web form for the Rudder Travel Calculator ported from the gist."""
    result = None
    chord_val = None
    if request.method == "POST":
        form = RudderCalculatorForm(request.POST)
        if form.is_valid():
            chord = form.cleaned_data["rudder_chord"]
            travel = form.cleaned_data["travel_deg"]
            solution = sas_solver(chord, travel)
            result = {"travel_in": solution}
            chord_val = chord
    else:
        form = RudderCalculatorForm()
    return render(
        request,
        "fs2020/rudder_calculator.html",
        {"form": form, "result": result, "chord_val": chord_val},
    )
