from django.utils.deconstruct import deconstructible
from django.core import validators

@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r"^(\+[1-9]{1}[0-9]{11})+$"