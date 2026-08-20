from django.urls import path

from . import views

app_name = "appcheck"

urlpatterns = [
    path("", views.home, name="home"),
    path("check/", views.check_app, name="check_app"),
    path("result/<int:pk>/", views.result, name="result"),
    path("past-checks/", views.past_checks, name="past_checks"),
]
