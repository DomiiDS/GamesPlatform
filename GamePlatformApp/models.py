from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='img/', default = 'profile.jpg')
    bio = models.CharField(max_length=250, default='A GamePlatform user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)