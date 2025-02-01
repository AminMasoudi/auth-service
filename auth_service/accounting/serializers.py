from rest_framework import serializers
from .validators import UsernameValidator

class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, validators=[UsernameValidator()]
        )
    password = serializers.CharField(required=True)