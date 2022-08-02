from django.db import models


# Create your models here.
class League(models.Model):
    """
    League model to store details related to each racing league.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        """ """
        return f"{self.name}"


class Track(models.Model):
    """ """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Driver(models.Model):
    """ """

    name = models.CharField(max_length=100)
    points = models.IntegerField()
    league = models.ManyToManyField(League)

    def increment_points(self, by: int):
        """
        Increment driver points.
        """

    def __str__(self):
        """ """
        return f"{self.name}"


class Race(models.Model):
    """ """

    name = models.CharField(max_length=100)
    track = models.ForeignKey(to="Track", on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    laps = models.IntegerField()
    day_race = models.BooleanField()
    raining = models.BooleanField()
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name}"
