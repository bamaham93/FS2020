from django.shortcuts import render
from media.models import Media, MediaFormat, MediaType
from media.forms import AddMediaForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    """ """
    context = {}
    return render(request, "media/index.html", context)


def movies(request):
    """ """
    movies = Media.objects.filter(type__name="Movie")
    context = {
        "movies": movies,
        # 'genres': movies.genres,
    }
    return render(request, "media/movies.html", context)


@login_required
def add_media(request):
    """
    """
    add_media_form = AddMediaForm()
    context = {
        'add_media_form': add_media_form
    }

    if request.method == "POST":
        # print("Posted!")
        form = AddMediaForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/media/add_media")
    elif request.method == "GET":
        # print("Got!")

    return render(request, "media/add_media.html", context)


def books(request):
    books = Media.objects.filter(type__name="Book")
    context = {"books": books}
    return render(request, "media/books.html", context)


def cds(request):
    """ """
    cds = Media.objects.filter(format__name="CD")
    context = {"cds": cds}
    return render(request, "media/cds.html", context)


def dvds(request):
    """ """
    dvds = Media.objects.filter(format__name="DVD")
    context = {
        "dvds": dvds,
    }
    return render(request, "media/dvds.html", context)


def amazon(request):
    """ """
    videos = Media.objects.filter(format__name="Amazon")
    context = {"videos": videos}
    return render(request, "media/amazon.html", context)


def youtube(request):
    videos = Media.objects.filter(format__name="YouTube")
    context = {
        "videos": videos,
    }
    return render(request, "media/youtube.html", context)


def digital_dl(request):
    """ """
    videos = Media.objects.filter(format__name="Digital Download")
    context = {"videos": videos}
    return render(request, "media/digital_dl.html", context)


def vhs(request):
    """ """
    vhs_s = Media.objects.filter(format__name="VHS")
    context = {"videos": vhs_s}
    return render(request, "media/vhs.html", context)

def sorted_by(request):
    """
    """
    context = {
        "media_query": Media.objects.all()
    }
    return render(request, 'media/sorted_by.html', context)
