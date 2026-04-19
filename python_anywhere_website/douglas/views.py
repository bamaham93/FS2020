""" """

"""
Deprecated: Douglas views removed. Functions left as simple placeholders
to avoid import errors; the app is no longer mounted in `urls.py`.
"""

from django.http import HttpResponse


def index(request):
    return HttpResponse("Douglas app retired.")


def nis_index(request):
    return HttpResponse("Douglas app retired.")


def standings(request):
    return HttpResponse("Douglas app retired.")


def add_race_result(request):
    return HttpResponse("Douglas app retired.")
