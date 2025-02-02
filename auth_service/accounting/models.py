from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.utils import timezone
import datetime
import logging
import uuid

from .validators import PhoneValidator, UsernameValidator
from .utils import create_otp_code

# Create your models here.
logger = logging.getLogger("django")


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

        if (
            (email is None)
            and (phone is None)
            and ((username := extra_fields.get("username")) is not None)
        ):
            if "@" in username:
                email = username
            else:
                phone = username

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

    @classmethod
    def get_user(cls: "User", username):
        return cls.objects.filter(
            models.Q(email=username) | models.Q(phone=username)
        ).first()

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


class OTPManager(models.Manager):
    def create(self, username: str):
        otp_type = "e" if "@" in username else "p"
        user = User.get_user(username)
        if not user:
            logger.warning(f"User with username '{username}' does not exist.")
            raise ValueError(f"User with username '{username}' does not exist.")
        ttl = settings.OTP_MAIL_TTL if "@" in username else settings.OTP_PHONE_TTL
        otp = self.model(otp_type=otp_type, user=user, ttl=ttl)
        otp.save(using=self._db)
        otp.send()
        logger.info(f"OTP created for user '{username}' (type: {otp_type}).")
        return otp


class OTP(models.Model):
    class OTP_TYPE(models.TextChoices):
        EMAIL = "e"
        PHONE = "p"

    otp_type = models.CharField(max_length=1, choices=OTP_TYPE)
    code = models.IntegerField(default=create_otp_code)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    ttl = models.IntegerField()

    objects = OTPManager()

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=self.ttl)

    def send(self):
        if self.otp_type == "e":
            self.send_mail()
        else:
            self.send_phone()

    def send_mail(self):
        logger.info(f"Sending OTP via email to {self.user.email}.")

    def send_phone(self):
        logger.info(f"Sending OTP via phone to {self.user.phone}.")
