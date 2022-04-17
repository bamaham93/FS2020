from django.shortcuts import render
from .models import Job, Technology

# Create your views here.
def index(request):
    context = {}
    return render(request, "resume/index.html", context)

def aviation(request):
    """
    Display aviation related education, work experience, and highlights.
    """
    context = {'aviation_jobs': Job.objects.filter(aviation=True).order_by("-start_date")}
    return render(request, "resume/aviation_experience.html", context)

def tech(request):
    """
    Tech resume, related experience, and highlights.
    """
    context = {'technologies': Technology.objects.all().order_by('-start_date')}
    return render(request, "resume/tech_experience.html", context)