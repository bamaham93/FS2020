from django.shortcuts import render
from .models import Job, Technology
from .forms import ContactMeForm
from logic.queries import JobQueries


# Create your views here.
def index(request):
    context = {}
    return render(request, "resume/index.html", context)


def aviation(request):
    """
    Display aviation related education, work experience, and highlights.
    """
    context = {
        # 'aviation_jobs': Job.objects.filter(aviation=True).order_by("-start_date")
        'aviation_jobs': JobQueries.get_aviation_jobs()
    }
    return render(request, "resume/aviation_experience.html", context)


def tech(request):
    """
    Tech resume, related experience, and highlights.
    """
    context = {
        'technologies': Technology.objects.all().order_by('-start_date'),
        # 'jobs': Job.objects.all().filter(aviation=False).order_by('-start_date')
        'jobs': JobQueries.get_tech_jobs()
    }
    return render(request, "resume/tech_experience.html", context)


def contact_me(request):
    """
    """
    form = ContactMeForm()
    context = {'form': form}
    if request.method == "POST":
        form = ContactMeForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'resume/contact_me.html', context)
