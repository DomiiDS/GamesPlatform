from django.db import models
from django.core.exceptions import ValidationError
import re

def ValidateUser(user):
    if re.fullmatch(r"^\w+$", user) == None:
        raise ValidationError(("Username must only contain alphanumerical characters or _"), code = "invalid")

def ValidatePassword(password):
    if re.fullmatch(r"^[^\s]+$", password) == None:
        raise ValidationError(("Password must not contain whitespaces"), code = "invalid")

def ValidateEmail(email):
    if re.fullmatch(r"^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$", email) == None:
        raise ValidationError(("Must be a valid email address"), code = "invalid")

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length = 100, validators=[ValidateUser])
    password = models.CharField(max_length = 100, validators=[ValidatePassword])
    email = models.CharField(max_length = 100, validators=[ValidateEmail])
    isdeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username