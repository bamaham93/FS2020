from django.shortcuts import render
# from .models import Race, League  # May be able to delete in favor of using the central logic.queries package.
from django.contrib.auth.decorators import login_required
from logic.queries import DriverQueries, RaceQueries, LeagueQueries


# Create your views here.
def index(request):
    """
    Keeping this to make a racing home page.
    """
    context = {
        # 'races' : Race.objects.all().filter().order_by('datetime'),
        'races': RaceQueries.get_races()
    }
    # context = {}
    return render(request, 'douglas/nis_index.html', context=context)


def nis_index(request):
    """
    """
    context = {'races': RaceQueries.get_races()}
    return render(request, "douglas/nis_index.html", context)


def standings(request):
    """
    """
    context = {
        # 'leagues' : League.objects.all(),
        'leagues': LeagueQueries.get_leagues(),
        'nis_drivers': DriverQueries.get_nis_drivers(),
        'ashoc_drivers': DriverQueries.get_ashoc_drivers(),
    }
    return render(request, "douglas/standings.html", context)


@login_required
def add_race_result(request):
    """
    View to add race results to database.
    """
    context = {}
    return render(request, "douglas/add_results.html", context=context)
