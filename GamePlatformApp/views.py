from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View, DetailView
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
#from matplotlib.style.core import available
from django.contrib.auth import get_user_model

from .models import User, Comment, Race, Horse, Bet, RouletteField, RouletteWheel, RouletteBet
from .forms import UserForm, ProfileForm, CommentForm, RoulettePickForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json, random

User = get_user_model()

SORTABLE_FIELDS = {
    'horse_won': 'horse_race_chips_won',
    'horse_lost': 'horse_race_chips_lost',
    'horse_games_won': 'horse_race_games_won',
    'horse_games_lost': 'horse_race_games_lost',
    'roulette_won': 'roulette_chips_won',
    'roulette_lost': 'roulette_chips_lost',
    'roulette_games_won': 'roulette_games_won',
    'roulette_games_lost': 'roulette_games_lost',
    'blackjack_won': 'blackjack_chips_won',
    'blackjack_lost': 'blackjack_chips_lost',
    'blackjack_games_won': 'blackjack_games_won',
    'blackjack_games_lost': 'blackjack_games_lost',
    'total_won': 'total_chips_won',
    'total_lost': 'total_chips_lost',
    'total_games_won': 'total_games_won',
    'total_games_lost': 'total_games_lost',
}

class HomeView(ListView):
    model = User
    paginate_by = 10
    template_name = 'GamePlatformApp/home.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('id')

class RegisterView(TemplateView):
    template_name = "GamePlatformApp/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("register_success"))

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class RegisterSuccessView(TemplateView):
    template_name = "GamePlatformApp/register_success.html"

class UserListView(ListView):
    model = User
    paginate_by = 10
    template_name = 'GamePlatformApp/users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('id')

class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'GamePlatformApp/users/user_form.html'
    success_url = '/users/'

    """def dispatch(self, request, *args, **kwargs):
        # Get the user being edited
        obj = self.get_object()

        # Prevent editing someone else's profile
        if obj != request.user:
            raise PermissionDenied("You cannot edit someone else's profile.")

        return super().dispatch(request, *args, **kwargs)"""

class UserDeleteView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.username += "<deleted_" + str(pk) + ">"
        user.save()
        return redirect('/users/')
    
class UserProfileView(DetailView):
    model = User
    template_name = 'GamePlatformApp/users/profile.html'
    context_object_name = 'profile_user'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile_user = self.get_object()
        context['comments'] = profile_user.comments_received.all()
        context['form'] = CommentForm()
        return context
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.object = self.get_object()
        profile_user = self.object
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.profile = profile_user
            comment.save()
        return redirect('user-profile', pk=profile_user.pk)


class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'GamePlatformApp/users/profile_form.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        # Get the user being edited
        obj = self.get_object()

        # Prevent editing someone else's profile
        if obj != request.user:
            raise PermissionDenied("You cannot edit someone else's profile.")

        return super().dispatch(request, *args, **kwargs)

class UserStatsView(DetailView):
    model = User
    template_name = 'GamePlatformApp/users/user_stats.html'
    context_object_name = 'profile_user'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        return context

class GamesListView(TemplateView):
    template_name = 'GamePlatformApp/games.html'

class RouletteView(TemplateView):
    template_name = 'GamePlatformApp/games/roulette_js.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['chips'] = user.chips
        context['user'] = user
        context['wheel'] = RouletteWheel.get_singleton()
        context['form'] = RoulettePickForm()
        wheel = RouletteWheel.get_singleton()
        last_win = wheel.fields.filter(won=True).first()
        context['winning_field'] = last_win
        return context
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            raise PermissionDenied("Log in to play games.")

        return super().dispatch(request, *args, **kwargs)

def start_roulette(request):
    if request.user.is_anonymous:
            raise PermissionDenied("Log in to play games.")

    wheel = RouletteWheel.get_singleton()

    fields = list(RouletteField.objects.all())
    if len(fields) < 37:
        red_numbers = {
            1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
        }

        fields = []
        for i in range(37):
            if i == 0:
                color = "green"
            elif i in red_numbers:
                color = "red"
            else:
                color = "black"

            fields.append(RouletteField(num=i, color=color))
            RouletteField.objects.create(RouletteField(num=i, color=color))

    RouletteField.objects.update(won=False)

    wheel.fields.set(fields)

    return redirect('roulette')

def roulette_resolve(request):
    wheel = RouletteWheel.get_singleton()

    winning_field = wheel.spin()

    bets = RouletteBet.objects.select_related("user").prefetch_related("fields")

    for bet in bets:
        bet.user.roulette_chips_bet += bet.amount
        bet.user.total_chips_bet += bet.amount
        payout = bet.resolve()
        if payout > 0:
            bet.user.chips += payout
            bet.user.roulette_chips_won += payout
            bet.user.roulette_games_won += 1
            bet.user.total_chips_won += payout
            bet.user.total_games_won += 1
            bet.user.save()

    bets.delete()  # clear bets after round

    return render(request, "GamePlatformApp/games/roulette.html", {
        "winning_field": winning_field,
        "chips": request.user.chips,
        "user": request.user,
    })

def roulette_bet(request):
    if request.method == "POST":
        field_ids = request.POST.getlist("fields")
        amount = int(request.POST.get("amount"))
        bet_type = int(request.POST.get("bet_type", 1))

        user = request.user
        fields = RouletteField.objects.filter(id__in=field_ids)

        if not fields.exists():
            return JsonResponse({"error": "No fields selected"}, status=400)

        if user.chips < amount:
            return JsonResponse({"error": "Not enough chips!"}, status=400)

        user.chips -= amount
        user.save()

        bet = RouletteBet.objects.create(
            user=user,
            amount=amount,
            bet_type=bet_type
        )
        bet.fields.set(fields)

        return redirect("roulette")

    return redirect("roulette")

@require_POST
def roulette_ajax(request):
    if request.user.is_anonymous:
        raise PermissionDenied("Log in to play games.")
    wheel = RouletteWheel.get_singleton()
    winning_field = wheel.spin()
    bets = RouletteBet.objects.select_related("user")
    for bet in bets:
        bet.user.roulette_chips_bet += bet.amount
        bet.user.total_chips_bet += bet.amount
        payout = bet.resolve()
        if payout > 0:
            bet.user.chips += payout
            profit = payout - bet.amount
            bet.user.roulette_chips_won += profit
            bet.user.roulette_games_won += 1
            bet.user.total_chips_won += profit
            bet.user.total_games_won += 1
            bet.user.roulette_highest_win = max(bet.user.roulette_highest_win, profit)
            bet.user.total_highest_win = max(bet.user.total_highest_win, profit)
        else:
            loss = bet.amount
            bet.user.roulette_games_lost += 1
            bet.user.roulette_chips_lost += loss
            bet.user.total_games_lost += 1
            bet.user.total_chips_lost += loss
            bet.user.roulette_highest_lost = max(bet.user.roulette_highest_lost, loss)
            bet.user.total_highest_lost = max(bet.user.total_highest_lost, loss)
        bet.user.save()
    bets.delete()
    return JsonResponse({"winning_number": winning_field.num,
                        "winning_color": winning_field.color,
                         "user_chips": request.user.chips,
                         })


class BlackjackView(TemplateView):
    template_name = 'GamePlatformApp/games/blackjack.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['chips'] = user.chips
        return context
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            raise PermissionDenied("Log in to play games.")

        return super().dispatch(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateChipsView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'You must login to update chips!'}, status=401)
        try:
            data = json.loads(request.body)
            new_chips = int(data.get('chips'))
            game = data.get('game', 'unknown')
            bet_amount = int(data.get('bet_amount', 0))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        try:
            user = request.user
            old_chips = user.chips
            user.chips = new_chips
            net_change = new_chips - old_chips

            # Update stats
            if game == 'blackjack':
                user.blackjack_chips_bet += bet_amount
                user.total_chips_bet += bet_amount
                if net_change > 0:
                    profit = net_change
                    user.blackjack_chips_won += profit
                    user.blackjack_games_won += 1
                    user.total_chips_won += profit
                    user.total_games_won += 1
                    user.blackjack_highest_win = max(user.blackjack_highest_win, profit)
                    user.total_highest_win = max(user.total_highest_win, profit)
                else:
                    loss = -net_change
                    user.blackjack_games_lost += 1
                    user.blackjack_chips_lost += loss
                    user.total_games_lost += 1
                    user.total_chips_lost += loss
                    user.blackjack_highest_lost = max(user.blackjack_highest_lost, loss)
                    user.total_highest_lost = max(user.total_highest_lost, loss)
            # For horse_race and roulette, handled in their resolve functions

            user.save()
            return JsonResponse({'success': True, 'chips': new_chips}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

# placeholderowe dodawanie koni
def add_horse(request):
    HORSE_NAMES = [
        "Jack", "Roberto", "Juan", "Jose",
        "Twilight Sparkle", "Rainbow Dash", "Applejack", "Pinkie Pie", "Fluttershy", "Rarity",
    ]
    HORSE_COLORS = ["normal", "sepia", "invert", "blue", "red", "green", "pink"]

    available_names = [name for name in HORSE_NAMES if not Horse.objects.filter(name=name).exists()]
    while available_names:
        name = random.choice(available_names)
        speed = 1.0
        color = random.choice(HORSE_COLORS)

        horse = Horse.objects.create(
            name=name,
            speed=speed,
            color=color
        )

        available_names = [name for name in HORSE_NAMES if not Horse.objects.filter(name=name).exists()]

    return redirect('games')


def start_race(request):
    if request.user.is_anonymous:
            raise PermissionDenied("Log in to play games.")

    # Resolve any unresolved bets as losses
    unresolved_bets = Bet.objects.filter(resolved=False)
    for bet in unresolved_bets:
        loss = bet.amount
        bet.user.horse_race_games_lost += 1
        bet.user.horse_race_chips_lost += loss
        bet.user.total_games_lost += 1
        bet.user.total_chips_lost += loss
        bet.user.horse_race_highest_lost = max(bet.user.horse_race_highest_lost, loss)
        bet.user.total_highest_lost = max(bet.user.total_highest_lost, loss)
        bet.user.horse_race_chips_bet += bet.amount
        bet.user.total_chips_bet += bet.amount
        bet.won = False
        bet.resolved = True
        bet.user.save()
        bet.save()

    race = Race.get_singleton()

    all_horses = list(Horse.objects.all())

    # wybiera losowo 3 konie do wyścigu
    if len(all_horses) < 3:
        selected_horses = all_horses
    else:
        selected_horses = random.sample(all_horses, 3)

    race.horses.set(selected_horses)

    return redirect('race-room')

def race_room(request):
    race = Race.get_singleton()
    bets = Bet.objects.filter(user=request.user, resolved=True).order_by('-id')[:5]
    chips = request.user.chips
    return render(request, 'GamePlatformApp/games/racing_room.html', {"race": race, "bets": bets, "chips": chips})

@csrf_exempt
def set_winner(request):
    if request.method == "POST":
        data = json.loads(request.body)
        winner_name = data.get("winner_name")
        try:
            winner = Horse.objects.get(name=winner_name)
        except Horse.DoesNotExist:
            return JsonResponse({"error": "No such horse"}, status=404)

        race = Race.get_singleton()
        race.winner = winner
        race.save()

        bets = Bet.objects.filter(resolved=False)
        for bet in bets:
            bet.user.horse_race_chips_bet += bet.amount
            bet.user.total_chips_bet += bet.amount
            if bet.horse == winner:
                winnings = bet.amount * 2
                bet.user.chips += winnings
                profit = bet.amount
                bet.user.horse_race_chips_won += profit
                bet.user.horse_race_games_won += 1
                bet.user.total_chips_won += profit
                bet.user.total_games_won += 1
                bet.user.horse_race_highest_win = max(bet.user.horse_race_highest_win, profit)
                bet.user.total_highest_win = max(bet.user.total_highest_win, profit)
                bet.won = True
            else:
                loss = bet.amount
                bet.user.horse_race_games_lost += 1
                bet.user.horse_race_chips_lost += loss
                bet.user.total_games_lost += 1
                bet.user.total_chips_lost += loss
                bet.user.horse_race_highest_lost = max(bet.user.horse_race_highest_lost, loss)
                bet.user.total_highest_lost = max(bet.user.total_highest_lost, loss)
                bet.won = False

            bet.resolved = True
            bet.user.save()
            bet.save()
        return JsonResponse({"success": True, "user_chips": request.user.chips})

def place_bet(request):
    if request.method == "POST":
        horse_id = request.POST.get("horse_id")
        amount = int(request.POST.get("amount"))

        horse = get_object_or_404(Horse, pk=horse_id)
        user = request.user

        if user.chips < amount:
            return JsonResponse({"error": "Not enough chips!"}, status=400)

        user.chips -= amount
        user.save()

        Bet.objects.create(
            user=user,
            horse=horse,
            amount=amount
        )

        return redirect("race-room")

    return redirect("race-room")

def leaderboard_view(request):
    sort_key = request.GET.get('sort', 'total_won')
    direction = request.GET.get('dir', 'desc')
    page_number = request.GET.get('page', 1)

    sort_field = SORTABLE_FIELDS.get(sort_key, 'total_chips_won')
    ordering = f"-{sort_field}" if direction == 'desc' else sort_field

    users = User.objects.all().order_by(ordering)

    paginator = Paginator(users, 25)  # 25 users per page
    page_obj = paginator.get_page(page_number)

    return render(request, 'GamePlatformApp/leaderboard.html', {
        'page_obj': page_obj,
        'users': users,
        'sort': sort_key,
    })