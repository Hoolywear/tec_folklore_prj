from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import *


# Create your views here.

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy('users:login')


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True


@login_required
def profile(request):
    return render(request, 'users/profile.html')
