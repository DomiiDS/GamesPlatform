from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View, DetailView
from django.urls import reverse_lazy, reverse
from .models import User, Comment
from .forms import UserForm, ProfileForm, CommentForm
from django.core.exceptions import PermissionDenied

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
