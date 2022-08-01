from django.shortcuts import render

# Create your views here.
def index(request):
    """
    """
    context = {}
    return render(request, 'prayer/index.html', context)


def new_message(request):
    """
    """
    context = {}
    return render(request, 'prayer/new_message.html', context)


def groups(request):
    """
    """
    context = {}
    return render(request, 'prayer/groups.html', context)

def prayer_requests(request):
    """

    """
    context = {}
    return render(request, 'prayer/prayer_request.html', context)