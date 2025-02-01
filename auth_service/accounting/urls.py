from django.urls import path
from .views import LoginView, logout
urlpatterns = [
    path("login/", view=LoginView.as_view(), name="simple_login"),
    path("logout/", logout, name="logout")
]