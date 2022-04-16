from django.db import models

# Create your models here.
class Track(models.Model):
    """
    """
    name = models.CharField(max_length=100)


class Race(models.Model):
    """
    """
    name = models.CharField(max_length=100)
    track = models.ForeignKey(to='Track', on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    laps = models.IntegerField()
    day_race = models.BooleanField()
    raining = models.BooleanField()