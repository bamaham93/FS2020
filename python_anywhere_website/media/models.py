"""

Descriptions were taken from:
https://www.studiobinder.com/blog/movie-genres-list
"""

from django.db import models
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Fieldset


# Create your models here.
class MediaFormat(models.Model):
    """ """

    name = models.CharField(max_length=100)

    def __str__(self):
        """ """
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class MediaType(models.Model):
    """ """

    name = models.CharField(max_length=100)

    def __str__(self):
        """ """
        return f"{self.name}"


class MediaGenre(models.Model):
    """ """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        """ """
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class MediaLocation(models.Model):
    """
    Description: description of the location of the storage location.
    Shelf Unit: Which shelving unit holds the item.
    Shelf: Which shelf on that unit holds the item.
    """

    description = models.TextField()
    shelf_unit = models.CharField(max_length=100)
    shelf = models.CharField(max_length=100)

    def __str__(self):
        """ """
        if self.shelf_unit and self.shelf:
            return f"{self.shelf_unit} {self.shelf}"
        elif self.shelf_unit:
            return f"{self.shelf_unit}"
        elif self.shelf:
            return f"{self.shelf}"
        else:
            return f"Unknown"


class Media(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True)
    description = models.TextField(blank=True, null=True)
    format = models.ForeignKey(MediaFormat, on_delete=models.CASCADE)
    type = models.ForeignKey(MediaType, on_delete=models.CASCADE, blank=True, null=True)
    genre = models.ManyToManyField(MediaGenre)
    storage_location = models.ForeignKey(
        MediaLocation, on_delete=models.CASCADE, blank=True, null=True
    )
    upc_code = models.CharField(max_length=100, blank=True, null=True)
    isbn_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """ """
        if self.title and self.subtitle:
            return f"{self.title} {self.subtitle}"
        else:
            return self.title

    class Meta:
        verbose_name_plural = "media"


class AddMediaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-mediaForm'
        self.helper.form_class = 'blueforms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'submit'

        self.helper.add_input(Fieldset('Hello, {{ username }}'))
        self.helper.add_input(Field('name', 'name'))
        self.helper.add_input(Field('isbn', 'isbn'))
        self.helper.add_input(Submit('submit', 'Submit'))
