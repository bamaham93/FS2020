from django.http import HttpResponse
from django.shortcuts import redirect


# Create your views here.
def redirect_home(request):
    """
    Redirects to the FS2020 app home page.
    """
    response = redirect("core_app:index")
    return response


def robots_txt(request):
    """
    Serve robots.txt for crawlers.
    """
    return HttpResponse(
        "User-agent: *\nDisallow: /prayer/\n",
        content_type="text/plain",
    )
