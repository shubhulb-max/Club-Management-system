import re

from django.core.exceptions import ValidationError


PHONE_DIGIT_PATTERN = re.compile(r"\D+")


def normalize_phone_number(phone_number):
    if phone_number is None:
        return phone_number

    normalized = PHONE_DIGIT_PATTERN.sub("", str(phone_number).strip())
    if not normalized:
        raise ValidationError("Phone number is required.")

    if len(normalized) == 12 and normalized.startswith("91"):
        normalized = normalized[2:]
    elif len(normalized) == 11 and normalized.startswith("0"):
        normalized = normalized[1:]

    if len(normalized) != 10:
        raise ValidationError(
            "Phone number must be a valid 10-digit Indian mobile number."
        )

    return normalized
