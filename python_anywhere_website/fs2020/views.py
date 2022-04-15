from django.shortcuts import render
from .models import Aircraft

# Create your views here.
def index(request):
    """
    FS2020 app home page.
    """
    context = {'title':'FS2020 Home'}
    context['aircraft'] =   Aircraft.objects.all()
    return render(request, 'fs2020/index.html', context)