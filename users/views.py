from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView, DeleteView

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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update_user.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):  # riconosco l'utente loggato
        return self.request.user


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    form_class = UserDeleteForm
    template_name = 'users/delete_user.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        return self.request.user
