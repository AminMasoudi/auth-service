import re
from django.utils.deconstruct import deconstructible
from django.core import validators
from django.core import exceptions
from django.utils.regex_helper import _lazy_re_compile


@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r"^((\+98|0)9\d{9})$"


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^((\+98|0)9\d{9})$"

    def __call__(self, value):
        try:
            validators.validate_email(value)
            return

        except exceptions.ValidationError:
            if re.match(self.regex, value) is None:
                raise exceptions.ValidationError(
                    "Enter a valid email address or phone number."
                )
            return
