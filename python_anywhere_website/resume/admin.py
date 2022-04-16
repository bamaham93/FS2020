from django.contrib import admin
from .models import Job, Certification

# Register your models here.
class JobAdmin(admin.ModelAdmin):
    """
    """
    list_display = ("title", "company", "location", "start_date", "end_date")


class CertificationAdmin(admin.ModelAdmin):
    """
    """
    list_display = ("name", "date_earned", "short_description")

admin.site.register(Job, JobAdmin)
admin.site.register(Certification, CertificationAdmin)