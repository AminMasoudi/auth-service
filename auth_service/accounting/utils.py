from django.conf import settings
import random

def create_otp_code() -> int:
    return random.randint(pow(10, settings.OTP_DIGIT - 1), pow(10, settings.OTP_DIGIT))
