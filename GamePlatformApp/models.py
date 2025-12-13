from django.db import models
from django.contrib.auth.models import AbstractUser
import random


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='img/', default = 'profile.jpg')
    bio = models.CharField(max_length=250, default='A GamePlatform user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chips = models.IntegerField(default=1000)

class Comment(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments_written')
    profile = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='comments_received')

class Horse(models.Model):
    name = models.CharField(max_length=50)
    speed = models.FloatField(default=1.0)
    color = models.CharField(max_length=20, default="normal")
    def __str__(self):
        return self.name

class Race(models.Model):
    horses = models.ManyToManyField(Horse, related_name='race_participants')
    winner = models.ForeignKey(Horse, null=True, blank=True, on_delete=models.CASCADE, related_name='race_winner')

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def run_race(self):
        horses = list(self.horses.all())
        chances = [h.speed for h in horses]
        self.winner = random.choices(horses, weights=chances)[0]
        self.save()

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    resolved = models.BooleanField(default=False)
    won = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.user.username} -> {self.horse.name} ({self.amount} chips)"

class RouletteField(models.Model):
    num = models.IntegerField(default=0)
    color = models.CharField(max_length=10, default="green")
    won = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.num} - {self.color}"

class RouletteWheel(models.Model):
    fields = models.ManyToManyField(RouletteField, related_name='wheel_fields')

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def spin(self):
        fields = list(self.fields.all())
        if not fields:
            raise RuntimeError("Roulette wheel has no fields attached")
        winning_field = random.choice(fields)
        winning_field.won = True
        winning_field.save()
        return winning_field

class RouletteBet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fields = models.ManyToManyField(RouletteField, related_name='user_fields')
    amount = models.IntegerField(default=0)
    bet_type = models.IntegerField(default=1)

    def resolve(self):
        fields = list(self.fields.all())
        if any([field.won for field in fields]):
            return self.amount + self.bet_type * self.amount
        else:
            return 0