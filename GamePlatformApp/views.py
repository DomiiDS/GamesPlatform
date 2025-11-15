from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View
from django.urls import reverse_lazy
from .models import User
from .forms import UserForm

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

class UserDeleteView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.username += "<deleted_" + str(pk) + ">"
        user.save()
        return redirect('/users/')
