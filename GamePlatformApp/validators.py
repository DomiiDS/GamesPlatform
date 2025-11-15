
from django.core.exceptions import ValidationError
import re


# def ValidateUser(user):
#     if re.fullmatch(r"^\w+$", user) is None:
#         raise ValidationError("Username must only contain alphanumerical characters or _", code ="invalid")


class NoWhitespacePasswordValidator:

    def validate(self, password, user=None):
        if re.fullmatch(r"^[^\s]+$", password) is None:
            raise ValidationError("Password must not contain whitespaces", code ="invalid")

    def get_help_text(self):
        return "Password must not contain whitespaces."


# def ValidateEmail(email):
#     if re.fullmatch(r"^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$", email) is None:
#         raise ValidationError("Must be a valid email address", code ="invalid")