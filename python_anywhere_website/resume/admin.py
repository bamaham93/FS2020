from tabnanny import verbose
from django.contrib import admin
from .models import Job, Certification, Technology, Message


# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    """
    list_display = ("title", "company", "location", "start_date", "end_date")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """
    """
    list_display = ("name", "date_earned", "short_description")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    """
    """
    verbose_name_plural = "Technologies"
    list_display = ("name", "start_date", "short_description")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    """

