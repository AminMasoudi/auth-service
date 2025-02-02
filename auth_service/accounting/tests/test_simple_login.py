from django.test import TestCase, Client
from django.urls import reverse
from accounting.models import User


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
