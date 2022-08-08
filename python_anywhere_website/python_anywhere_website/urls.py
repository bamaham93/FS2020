"""python_anywhere_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# from django.shortcuts import redirect
from .views import redirect_home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", redirect_home),
    path("home/", include("core.urls", namespace="core")),
    path("fs2020/", include("fs2020.urls", namespace="fs2020")),
    path("racing/", include("douglas.urls", namespace="racing")),
    path("resume/", include("resume.urls", namespace="resume")),
    path("prayer/", include("prayer.urls", namespace="prayer")),
    path("core/", include("django.contrib.auth.urls")),
    path("core/", include("core.urls", namespace="core")),
    path('media/', include('media.urls', namespace="media")),

]
