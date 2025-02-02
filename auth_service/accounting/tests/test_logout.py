from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


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
