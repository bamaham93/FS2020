"""
Database queries common to
"""

from douglas.models import Driver, Race, League
from resume.models import Job

# from django.contrib.auth.models import User, Group


class DriverQueries:
    """ """

    @staticmethod
    def get_nis_drivers():
        """
        Returns a Django QuerySet
        """
        drivers = Driver.objects.filter(
            league__name="NAPA Indycar Series - Forza Motorsports 7"
        )
        return drivers

    @staticmethod
    def get_ashoc_drivers():
        """
        Returns a django QuerySet
        """
        drivers = Driver.objects.filter(
            league__name="Ashoc Indy Lights Challenge - Forza Motorsports 7"
        )
        return drivers


class RaceQueries:
    """ """

    @staticmethod
    def get_races():
        """
        A list of all races in all leagues, ordered by datetime.
        """
        races = Race.objects.all().filter().order_by("datetime")
        return races

    @staticmethod
    def get_nis_races():
        """
        Returns Django QuerySet object of NIS races ordered by date.
        """
        races = (
            Race.objects.all()
            .filter(league__name="NAPA Indycar Series - Forza Motorsports 7")
            .order_by("datetime")
        )
        return races

    @staticmethod
    def get_ashoc_races():
        """
        Returns Django QuerySet of Ashoc races ordered by date.
        """
        races = (
            Race.objects.all()
            .filter("Ashoc Indy Lights Challenge - Forza Motorsports 7")
            .order_by("datetime")
        )
        return races


class LeagueQueries:
    """
    Contains a set of queries related to Douglas League model.
    """

    @staticmethod
    def get_leagues():
        """
        Get a QuerySet object of all races.
        """
        leagues = League.objects.all()
        return leagues


class JobQueries:
    """
    Contains  a set of queries related to the Resume Jobs model.
    """

    @staticmethod
    def get_aviation_jobs():
        """
        Returns a QuerySet of aviation jobs.
        """
        jobs = Job.objects.all().filter(aviation=True).order_by("-start-date")
        return jobs

    @staticmethod
    def get_tech_jobs():
        """
        Returns QuerySet of other-than-aviation jobs.
        """
        jobs = Job.objects.all().filter(aviation=False).order_by("-start-date")
        return jobs
