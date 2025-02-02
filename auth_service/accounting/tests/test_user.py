from django.test import TestCase
from ..models import User


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
