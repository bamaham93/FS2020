from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Job(models.Model):
    """
    Jobs and positions held.
    """

    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField()
    company = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    aviation = models.BooleanField()

    def __str__(self):
        """
        Human readable name.
        """
        return f"{self.title} at {self.company}"


class Certification(models.Model):
    """
    Certificates and skills earned that do not deserve a plane in education, but are relevant.
    """

    name = models.CharField(max_length=100)
    earned_from = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField(blank=True)
    date_earned = models.DateField()

    class Field(models.TextChoices):
        """ """

        AVIATION = "AVIA", _("Aviation")
        TECH = "TECH", _("Technology")

    field = models.CharField(
        max_length=4, choices=Field.choices, default=Field.AVIATION
    )

    def __str__(self):
        """ """
        return f"{self.name}"


class Technology(models.Model):
    """ """

    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)

    def __str(self):
        """ """
        return f"{self.name}"


class Message(models.Model):
    """ """

    from_email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=254)
    message = models.TextField()

    def __str__(self):
        """ """
        return f"{self.from_email}: {self.subject}"
