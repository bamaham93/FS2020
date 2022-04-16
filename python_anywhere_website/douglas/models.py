from django.db import models

# Create your models here.
class Track(models.Model):
    """
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Race(models.Model):
    """
    """
    name = models.CharField(max_length=100)
    track = models.ForeignKey(to='Track', on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    laps = models.IntegerField()
    day_race = models.BooleanField()
    raining = models.BooleanField()

    def __str__(self):
        return f"{self.name}"


class Driver(models.Model):
    """
    """
    name = models.CharField(max_length=100)
    points = models.IntegerField()

    def __str__(self):
        """
        """
        return f"{self.name}"