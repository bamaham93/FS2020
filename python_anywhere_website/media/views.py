from django.shortcuts import render
from media.models import Media, MediaFormat, MediaType


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
