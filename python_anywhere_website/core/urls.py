from django.urls import path
from .views import SignUpView
from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
