from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View, DetailView
from django.urls import reverse_lazy, reverse
from matplotlib.style.core import available

from .models import User, Comment, Race, Horse, Bet
from .forms import UserForm, ProfileForm, CommentForm
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json, random

class HomeView(ListView):
    model = User
    template_name = 'GamePlatformApp/home.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True)

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
    template_name = 'GamePlatformApp/users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True)

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

class BlackjackView(TemplateView):
    template_name = 'GamePlatformApp/games/blackjack.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['chips'] = user.chips
        return context

@method_decorator(csrf_exempt, name='dispatch')
class UpdateChipsView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'You must login to update chips!'}, status=401)
        try:
            data = json.loads(request.body)
            new_chips = int(data.get('chips'))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        try:
            user = request.user
            user.chips = new_chips
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
    race = Race.get_singleton()

    all_horses = list(Horse.objects.all())

    # wybiera losowo 3 konie do wyścigu
    if len(all_horses) < 3:
        selected_horses = all_horses
    else:
        selected_horses = random.sample(all_horses, 3)

    race.horses.set(selected_horses)

    #co to wgl za losowanie zwycięzcy przed wyścigiem lol
    #race.run_race()
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
            if bet.horse == winner:
                bet.user.chips += bet.amount * 2
                bet.won = True
            else:
                bet.won = False

            bet.resolved = True
            bet.user.save()
            bet.save()
        return JsonResponse({"success": True})

def place_bet(request):
    if request.method == "POST":
        horse_id = request.POST.get("horse_id")
        amount = int(request.POST.get("amount"))

        horse = get_object_or_404(Horse, pk=horse_id)
        user = request.user

        if user.chips < amount:
            return JsonResponse({"error": "Za mało chipsów!"}, status=400)

        user.chips -= amount
        user.save()

        Bet.objects.create(
            user=user,
            horse=horse,
            amount=amount
        )

        return redirect("race-room")

    return redirect("race-room")
