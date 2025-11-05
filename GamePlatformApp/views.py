from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .forms import UserForm

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