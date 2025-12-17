from django.test import TestCase
from django.contrib.auth import get_user_model
from GamePlatformApp.models import RouletteWheel, RouletteField, RouletteBet
from django.urls import reverse
#
User = get_user_model()
class RouletteBetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', chips=1000)
        self.client.login(username="test", password="test")
        self.field = RouletteField.objects.create(num=13, color='red', won=False)
        self.bet = RouletteBet.objects.create(user=self.user, amount=100, bet_type=1)
        self.bet.fields.add(self.field)
    def test_payout(self):
        self.field.won = True
        self.bet.won = True
        self.bet.save()
        self.field.save()
        payout = self.bet.resolve()
        self.assertGreater(payout, 0)
    def test_losing_bet_returns_zero(self):
        self.field.won = False
        self.bet.won = False
        self.bet.save()
        self.field.save()
        payout = self.bet.resolve()
        self.assertEqual(payout, 0)
    def test_bet_fails_if_not_enough_chips(self):
        response = self.client.post( reverse("roulette-bet"), { "fields": [self.field.id], "amount": 1500 } )
        self.assertEqual(response.status_code, 400)