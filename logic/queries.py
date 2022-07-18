"""
"""

from douglas.models import Driver, Race, League
from Django.db import QuerySet


class DriverQueries:
    """
    """

    @staticmethod
    def get_nis_drivers() -> QuerySet:
        """
        Returns a Django QuerySet
        """
        drivers = Driver.objects.filter(league__name='NAPA Indycar Series - Forza Motorsports 7')
        return drivers

    @staticmethod
    def get_ashoc_drivers() -> QuerySet:
        """
        Returns a django QuerySet
        """
        drivers = Driver.objects.filter(league__name='Ashoc Indy Lights Challenge - Forza Motorsports 7')
        return drivers


class RaceQueries:
    """
    """

    @staticmethod
    def get_races() -> QuerySet:
        """
        A list of all races in all leagues, ordered by datetime.
        """
        races = Race.objects.all().filter().order_by('datetime')
        return races


    @staticmethod
    def get_nis_races() -> QuerySet:
        """
        Returns Django QuerySet object of NIS races ordered by date.
        """
        races = Race.objects.all().filter(league__name='NAPA Indycar Series - Forza Motorsports 7').order_by('datetime')
        return races


    @staticmethod
    def get_ashoc_races() -> QuerySet:
        """
        Returns Django QuerySet of Ashoc races ordered by date.
        """
        races = Race.objects.all().filter('Ashoc Indy Lights Challenge - Forza Motorsports 7').order_by('datetime')
        return races


class LeagueQueries:
    """
    """

    @staticmethod
    def get_leagues() -> QuerySet:
        """
        Get a QuerySet object of all races.
        """
        leagues = League.objects.all()
        return leagues
