from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View, DetailView
from django.urls import reverse_lazy
from .models import User
from .forms import UserForm
from django.core.exceptions import PermissionDenied

class HomeView(TemplateView):
    template_name = "GamePlatformApp/home.html"

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