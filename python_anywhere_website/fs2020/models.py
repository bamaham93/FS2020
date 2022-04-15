from random import choices
from django.db import models

# Create your models here.
class Aircraft(models.Model):
    STATUS_CHOICES = (('Tied Down', 'Tied Down'), ('Pre-Flight', 'Pre-Flight'), ('In Flight', 'In Flight'))
    # MedalType = models.TextChoices('MedalType', 'GOLD SILVER BRONZE')
    n_num = models.CharField(max_length=10)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    icao_location = models.CharField(max_length=100)
    status = models.CharField(blank=True, null=True, choices=STATUS_CHOICES, max_length=100)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.n_num}"
    
    class Meta():
        verbose_name_plural = "Aircraft"


class Flight(models.Model):
    RULES_CHOICES = (('VFR', 'VFR'), ('IFR', 'IFR'))
    rules = models.CharField(max_length=100, choices=RULES_CHOICES)
    n_num = models.ForeignKey(to="Aircraft", on_delete=models.CASCADE)
    icao_origin = models.CharField(max_length=10)
    departure_datetime = models.DateTimeField()
    altitude = models.IntegerField()
    route = models.TextField()
    icao_destination = models.CharField(max_length=10)
    