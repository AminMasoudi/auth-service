from django.contrib.auth.backends import BaseBackend
from .models import User


class PasswordAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=..., password=..., **kwargs):
        user = User.objects.filter(email=username) | User.objects.filter(phone=username)
        user = user.first()
        if user is None:
            return
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
