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
from django.conf import settings
from django.conf.urls.static import static

# from django.shortcuts import redirect
from .views import redirect_home
from bible.urls import api_urlpatterns as bible_api_urls
from prayer import views as prayer_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", redirect_home),
    # core_app is available under /core_app/ (auth and app URLs)
    # Removed duplicate include at /home/ to avoid namespace collision
    path("fs2020/", include("fs2020.urls", namespace="fs2020")),
    path("resume/", include("resume.urls", namespace="resume")),
    path("prayer/", include("prayer.urls", namespace="prayer")),
    path("bible/", include("bible.urls", namespace="bible")),
    path("core_app/", include("django.contrib.auth.urls")),
    path("core_app/", include("core_app.urls", namespace="core_app")),
    path("media/", include("media_app.urls", namespace="media")),
    path("finance/", include("finance.urls", namespace="finance")),
    path("photography/", include("photography.urls", namespace="photography")),
    path("api/webhooks/twilio/sms/", prayer_views.twilio_sms_webhook, name="twilio_sms_webhook"),
]

# Add Bible API URLs (not under /bible/ prefix)
urlpatterns += bible_api_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
