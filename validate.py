import re
from tortoise.validators import Validator
from tortoise.exceptions import ValidationError


class UKMobileNumberValidator(Validator):
    def __call__(self, value):
        # Regex to match UK mobile numbers: +44 or 07 followed by 9 digits
        if not re.match(r"^(\+44|0)7\d{9}$", value):
            raise ValidationError(
                "Invalid UK mobile number. Must be a valid number starting with +44 or 07.")
