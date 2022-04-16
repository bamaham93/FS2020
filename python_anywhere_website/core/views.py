from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Website home page.
    """
    context = {}
    return render(request, 'core/index.html', context)