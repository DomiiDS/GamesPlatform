from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='img/', default = 'profile.jpg')
    bio = models.CharField(max_length=250, default='A GamePlatform user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments_written')
    profile = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='comments_received')