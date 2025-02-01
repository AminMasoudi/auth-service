from django.urls import path
from .views import LoginView
urlpatterns = [
    path("login/", view=LoginView.as_view(), name="simple_login"),
    
]