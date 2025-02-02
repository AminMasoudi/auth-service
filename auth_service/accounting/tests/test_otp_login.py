from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import datetime
from ..models import User, OTP


class OTPTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123", phone="09123456789"
        )
        self.client = Client()

    def test_otp_creation_for_email(self):
        otp = OTP.objects.create(username="test@example.com")
        self.assertEqual(otp.otp_type, "e")
        self.assertEqual(otp.user, self.user)
        self.assertFalse(otp.is_expired())

    def test_otp_creation_for_phone(self):
        otp = OTP.objects.create(username="09123456789")
        self.assertEqual(otp.otp_type, "p")
        self.assertEqual(otp.user, self.user)
        self.assertFalse(otp.is_expired())

    def test_otp_creation_for_invalid_user(self):
        with self.assertRaises(ValueError):
            OTP.objects.create(username="invalid@example.com")

    def test_otp_verification_success(self):
        otp = OTP.objects.create(username="test@example.com")
        response = self.client.post(
            reverse("otp-verify", kwargs={"username": "test@example.com"}),
            data={"code": str(otp.code)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.user.username)

    def test_otp_verification_expired(self):
        otp = OTP.objects.create(username="test@example.com")
        otp.created_at = timezone.now() - datetime.timedelta(minutes=otp.ttl + 1)
        otp.save()
        response = self.client.post(
            reverse("otp-verify", kwargs={"username": "test@example.com"}),
            data={"code": str(otp.code)},
        )
        self.assertEqual(response.status_code, 400)

    def test_otp_verification_invalid_code(self):
        OTP.objects.create(username="test@example.com")
        response = self.client.post(
            reverse("otp-verify", kwargs={"username": "test@example.com"}),
            data={"code": "00000"},
        )
        self.assertEqual(response.status_code, 400)

    def test_otp_deletion_after_verification(self):
        otp = OTP.objects.create(username="test@example.com")
        self.client.post(
            reverse("otp-verify", kwargs={"username": "test@example.com"}),
            data={"code": str(otp.code)},
        )
        self.assertFalse(OTP.objects.filter(id=otp.id).exists())
