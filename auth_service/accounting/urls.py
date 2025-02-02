from django.urls import path
from .views import LoginView, logout, OTPView

urlpatterns = [
    path("login/", view=LoginView.as_view(), name="simple_login"),
    path("logout/", logout, name="logout"),
    path("otp/<str:username>", OTPView.verify_otp, name="otp-verify"),
    path("otp/", OTPView.create, name="otp-create"),
]
