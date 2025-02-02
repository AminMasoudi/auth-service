from rest_framework import serializers
from .validators import UsernameValidator
from .models import OTP


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, validators=[UsernameValidator()])
    password = serializers.CharField(required=True)


class OTPCreateSerializer(serializers.ModelSerializer):
    username = username = serializers.CharField(
        required=True, validators=[UsernameValidator()]
    )

    class Meta:
        model = OTP
        fields = ("username",)


class OTPLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
