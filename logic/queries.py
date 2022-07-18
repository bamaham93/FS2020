"""
"""

# from .python_anywhere_website.douglas.models import Driver
from douglas.models import Driver, Race, League


class DriverQueries:
    """
    """

    @staticmethod
    def get_nis_drivers():
        """
        Returns a Django QuerySet
        """
        drivers = Driver.objects.filter(league__name='NAPA Indycar Series - Forza Motorsports 7')
        return drivers

    @staticmethod
    def get_ashoc_drivers():
        """
        Returns a django QuerySet
        """
        drivers = Driver.objects.filter(league__name='Ashoc Indy Lights Challenge - Forza Motorsports 7')
        return drivers


class RaceQueries:
    """
    """

    @staticmethod
    def get_races():
        """
        A list of all races in all leagues, ordered by datetime.
        """
        races = Race.objects.all().filter().order_by('datetime')
        return races


class LeagueQueries:
    """
    """

    @staticmethod
    def get_leagues():
        leagues = League.objects.all()
        return leagues
