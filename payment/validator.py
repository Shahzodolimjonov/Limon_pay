import re

from django.utils import timezone
from django.core.exceptions import ValidationError


def card_number_validator(value):
    if not re.match(r'^\d{16}$', value):
        raise ValidationError("Enter a valid card number.")
