from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PrayerProfile(models.Model):
    """
    Extends the Django User in ways that are specific to the prayer requests app.
    """

    user = models.OneToOneField(User, models.CASCADE)


class Person(models.Model):
    """
    A person that may be contacted for the prayer requests contact chain.
    """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(
        max_length=50, null=True, blank=True
    )  # TODO check if better way to validate.
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        """ """
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "People"


class PrayerGroup(models.Model):
    """
    Pre-assembled group of people that can be contacted, such as membership roll,
    """

    name = models.CharField(max_length=50)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField(blank=True, null=True)
    people = models.ManyToManyField(Person)

    def __str__(self):
        """ """
        return f"{self.name}"
