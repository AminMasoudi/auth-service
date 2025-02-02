from django.contrib.auth import authenticate, login, logout as log_out
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
from .serializers import (
    PasswordLoginSerializer,
    OTPCreateSerializer,
    OTPLoginSerializer,
)
from .models import OTP, User

# Create your views here.

logger = logging.getLogger("django")


class LoginView(APIView):
    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response("wrong credentials", status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({"username": user.username, "id": user.id})


@api_view(["POST"])
def logout(request):
    if request.user.is_authenticated:
        log_out(request)
    return Response("ok")


class OTPView:

    @api_view(["POST"])
    @staticmethod
    def create(request, *args, **kwargs):
        serializer = OTPCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            username = serializer.validated_data["username"]
            OTP.objects.create(username=username)
            logger.info(f"OTP created for {serializer.validated_data['username']}.")
            return Response(
                f"OTP code sent to {serializer.validated_data['username']}",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.warning(f"Error creating OTP: {e}")
            return Response(
                f"otp code sent to {serializer.validated_data["username"]}",
                status=status.HTTP_200_OK,
            )


    @api_view(["POST"])
    @staticmethod
    def verify_otp(request, username):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.get_user(username)
        if user is None:
            return Response("wrong otp or username", status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.objects.filter(user=user).last()
        if (
            (otp is not None)
            and (str(otp.code) == serializer.validated_data["code"])
            and (not otp.is_expired())
        ):
            login(request, user)
            otp.delete()
            return Response({"username": user.username, "id": user.id})
        return Response("wrong otp or username", status=status.HTTP_400_BAD_REQUEST)