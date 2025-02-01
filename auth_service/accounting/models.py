from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
import uuid

from .validators import PhoneValidator, UsernameValidator

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, phone, email, password, force=False, **extra_fields):
        if "username" in extra_fields:
            extra_fields.pop("username")

        assert password != None, "password is required"
        password = make_password(password)
        username = email or phone
        user = self.model(
            username=username,
            phone=phone,
            email=email,
            password=password,
            **extra_fields,
        )
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, password, phone=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
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

    username_validator = UsernameValidator()

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
    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        help_text=_("Required. in forms of phone or email."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def clean(self):
        if (self.email is None) and (self.phone is None):
            raise ValidationError("require email or phone")
        return super().clean()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        db_table = "Users"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(email__isnull=False),
                name="unique_non_null_email",
            ),
            models.UniqueConstraint(
                fields=["phone"],
                condition=models.Q(phone__isnull=False),
                name="unique_non_null_phone",
            ),
        ]
