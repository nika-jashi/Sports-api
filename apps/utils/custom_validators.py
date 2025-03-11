import re

from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def contains_digits(field: str) -> None:
    if not re.search(r"\d", field):
        raise ValidationError(
            _("This field must contain at least one digit")
        )


def does_not_contains_symbols(field: str) -> None:
    if re.search(r"\W", field):
        raise ValidationError(
            _("This field must not contain any symbols like: ! @ # $ % ^ &")
        )


def does_not_contains_whitespace(field: str) -> None:
    if re.search(r"\s", field):
        raise ValidationError(
            _("This field must not contain any whitespaces.")
        )


def contains_uppercase(field: str) -> None:
    if not re.search(r"[A-Z]", field):
        raise ValidationError(
            _("This field must contain at least one uppercase character.")
        )


def contains_lowercase(field: str) -> None:
    if not re.search(r"[a-z]", field):
        raise ValidationError(
            _("This field must contain at least one lowercase character.")
        )