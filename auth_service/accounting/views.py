from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PasswordLoginSerializer

# Create your views here.


class LoginView(APIView):
    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response("wrong credentials", status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response(
            {"username": user.username, "id": user.id}
        )