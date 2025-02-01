from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
import uuid

from .validators import PhoneValidator

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, phone, email, password, force=False, **extra_fields):

        assert password != None, "password is None"
        password = make_password(password)
        user = self.model(phone=phone, email=email, password=password, **extra_fields)
        if not force:
            user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, password, phone=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        if "username" in extra_fields:
            extra_fields.pop("username")
        return self._create_user(phone, email, password, **extra_fields)

    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(
            phone=phone, email=email, password=password, force=True, **extra_fields
        )


class User(AbstractUser):

    id = models.UUIDField(
        _("Id"),
        primary_key=True,
        db_column="user_id",
        db_index=True,
        auto_created=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    phone = models.CharField(
        _("Phone Number"),
        max_length=13,
        blank=True,
        null=True,
        validators=[PhoneValidator()],
    )
    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)
    username = None
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    @property
    def username_type(self): ...

    def clean(self):
        if (self.email is None) and (self.phone is None):
            raise ValidationError("require email or phone")

        return super().clean()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        unique_together = [["email", "phone"]]
        db_table = "Users"
