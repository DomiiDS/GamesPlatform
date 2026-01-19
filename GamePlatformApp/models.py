from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import math


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='img/', default = 'profile.jpg')
    bio = models.CharField(max_length=250, default='A GamePlatform user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chips = models.IntegerField(default=1000)
    
    # Horse Race Stats
    horse_race_chips_bet = models.IntegerField(default=0)
    horse_race_chips_won = models.IntegerField(default=0)
    horse_race_games_won = models.IntegerField(default=0)
    horse_race_games_lost = models.IntegerField(default=0)
    horse_race_chips_lost = models.IntegerField(default=0)
    horse_race_highest_win = models.IntegerField(default=0)
    horse_race_highest_lost = models.IntegerField(default=0)
    
    # Roulette Stats
    roulette_chips_bet = models.IntegerField(default=0)
    roulette_chips_won = models.IntegerField(default=0)
    roulette_games_won = models.IntegerField(default=0)
    roulette_games_lost = models.IntegerField(default=0)
    roulette_chips_lost = models.IntegerField(default=0)
    roulette_highest_win = models.IntegerField(default=0)
    roulette_highest_lost = models.IntegerField(default=0)
    
    # Blackjack Stats
    blackjack_chips_bet = models.IntegerField(default=0)
    blackjack_chips_won = models.IntegerField(default=0)
    blackjack_games_won = models.IntegerField(default=0)
    blackjack_games_lost = models.IntegerField(default=0)
    blackjack_chips_lost = models.IntegerField(default=0)
    blackjack_highest_win = models.IntegerField(default=0)
    blackjack_highest_lost = models.IntegerField(default=0)
    
    # Total Stats
    total_chips_bet = models.IntegerField(default=0)
    total_chips_won = models.IntegerField(default=0)
    total_games_won = models.IntegerField(default=0)
    total_games_lost = models.IntegerField(default=0)
    total_chips_lost = models.IntegerField(default=0)
    total_highest_win = models.IntegerField(default=0)
    total_highest_lost = models.IntegerField(default=0)

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
        winning_field = RouletteField.objects.filter(won=True).first()

        if not winning_field or not fields:
            return 0

        # STRAIGHT NUMBER BET
        if self.bet_type == 1:
            if any(field.won for field in fields):
                return self.amount * 2
            return 0

        # HIGH / LOW 
        if self.bet_type == 2:
            pivot = fields[0].num
            if winning_field.num > pivot:
                return self.amount * 2
            return 0

        # EVEN / ODD
        if self.bet_type == 3:
            pivot = fields[0].num

            # zero always loses
            if winning_field.num == 0:
                return 0

            if (winning_field.num % 2) == (pivot % 2):
                return self.amount * 2
            return 0

        return 0


