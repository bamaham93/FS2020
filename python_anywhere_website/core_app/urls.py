from django.urls import path
from .views import SignUpView, privacy_policy
from . import views

app_name = "core_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
]
