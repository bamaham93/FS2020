"""

"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from logic.queries import DriverQueries, RaceQueries, LeagueQueries
from logic.users_groups import is_group


# Create your views here.
def index(request):
    """
    Keeping this to make a racing home page.
    """
    context = {"races": RaceQueries.get_races()}
    return render(request, "douglas/nis_index.html", context=context)


def nis_index(request):
    """ """
    context = {"races": RaceQueries.get_races()}
    return render(request, "douglas/nis_index.html", context)


def standings(request):
    """ """
    context = {
        "leagues": LeagueQueries.get_leagues(),
        "nis_drivers": DriverQueries.get_nis_drivers(),
        "ashoc_drivers": DriverQueries.get_ashoc_drivers(),
        "is_staff": is_group(request.user, "Staff"),
    }
    return render(request, "douglas/standings.html", context)


@login_required
def add_race_result(request):
    """
    View to add race results to database.
    """
    context = {}
    return render(request, "douglas/add_results.html", context=context)
