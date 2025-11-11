from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, UpdateView, View
from django.urls import reverse_lazy
from .forms import UserForm
from .models import User

# Create your views here.

class Welcome(TemplateView):
    template_name = "GamePlatformApp/welcome.html"

class Login(TemplateView):
    template_name = "GamePlatformApp/login.html"

class Register(TemplateView):
    template_name = "GamePlatformApp/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return redirect(reverse_lazy("register_success"))

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class RegisterSuccess(TemplateView):
    template_name = "GamePlatformApp/register_success.html"

class UserListView(ListView):
    model = User
    template_name = 'GamePlatformApp/users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(isdeleted=False)

class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'GamePlatformApp/users/user_form.html'
    success_url = '/users/'

class UserDeleteView(View):
    def post(self,request,pk):
        user = get_object_or_404(User,pk=pk)
        user.isdeleted = True
        user.save()
        return redirect('/users/')

