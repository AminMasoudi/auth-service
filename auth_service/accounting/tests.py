from django.test import TestCase, Client
from .models import User, OTP
from django.urls import reverse
from django.utils import timezone
import datetime


# Create your tests here.
class TestUserModel(TestCase):
    def create(self, **values):
        user = err = None
        try:
            user = User.objects.create_user(**values)
        except TypeError as e:
            err = e
        except Exception as e:
            err = e
        return user, err

    def test_model_creation(self):
        # create user properly
        user, err = self.create(
            password="1234567890", phone="+989123456789", email="test@mock.com"
        )
        assert user is not None
        assert err is None

    def test_create_user_without_email_and_phone(self):
        user, err = self.create()
        assert user is None
        assert err is not None
        assert type(err) is TypeError

    def test_create_user_without_password(self):
        user, err = self.create(email="test@mock.com")
        assert user is None
        assert err is not None
        assert type(err) is TypeError

    def test_create_user_without_email(self):
        user, err = self.create(password="1234567890", phone="+989123456789")
        assert user is not None
        assert err is None

    def test_create_user_without_phone_number(self):
        user, err = self.create(password="1234567890", email="test@mock.com")
        assert user is not None
        assert err is None

    def test_validations(self):
        """Maybe later :))) means never"""
        ...


class SimpleLoginTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            password="testpassword123", email="test@example.com", phone="+989123456789"
        )
        self.client = Client()

    def test_login_with_email_success(self):
        response = self.client.post(
            reverse("simple_login"),
            {"username": "test@example.com", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_with_phone_success(self):
        response = self.client.post(
            reverse("simple_login"),
            {"username": "+989123456789", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_with_incorrect_username(self):
        response = self.client.post(
            reverse("simple_login"),
            {"username": "wrong@example.com", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_login_with_incorrect_password(self):
        response = self.client.post(
            reverse("simple_login"),
            {"username": "test@example.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_login_with_missing_username(self):
        # Test login with missing username
        response = self.client.post(
            reverse("simple_login"), {"password": "testpassword123"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_login_with_missing_password(self):
        # Test login with missing password
        response = self.client.post(
            reverse("simple_login"), {"username": "test@example.com"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_login_for_only_email_users(self):
        User.objects.create_user(email="test@mock.com", password="test@123")
        response = self.client.post(
            reverse("simple_login"),
            {"username": "test@mock.com", "password": "wrong@123"},
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            reverse("simple_login"),
            {"username": "test@mock.com", "password": "test@123"},
        )
        self.assertEqual(response.status_code, 200)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@mock.com", password="testpassword123"
        )
        self.client = Client()

    def test_logout_success(self):
        """
        Test that a logged-in user can log out successfully.
        """
        self.client.login(username="test@mock.com", password="testpassword123")
        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.post(reverse("logout"))

        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertEqual(response.status_code, 200)

    def test_logout_without_login(self):
        """
        Test that logging out without being logged in does not cause errors.
        """
        response = self.client.post(reverse("logout"))
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertEqual(response.status_code, 200)


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
