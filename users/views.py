from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView, DeleteView

from .forms import *


# Create your views here.

class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    success_message = "Utente creato correttamente!"
    template_name = "users/register.html"
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        # redirect alla home se già loggato
        if request.user.is_authenticated:
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(SuccessMessageMixin, LoginView):
    authentication_form = LoginForm
    success_message = "Login avvenuto con successo!"
    template_name = "users/login.html"
    redirect_authenticated_user = True


@login_required
def profile(request):
    return render(request, 'users/profile.html')


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = "Il profilo è stato aggiornato correttamente"
    template_name = 'users/update_user.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):  # riconosco l'utente loggato
        return self.request.user


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    form_class = UserDeleteForm
    success_message = "L'account è stato eliminato correttamente"
    template_name = 'users/delete_user.html'
    success_url = reverse_lazy('users:register')

    def get_object(self):
        return self.request.user


class UserChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    form_class = UserChangePasswordForm
    success_message = "Password cambiata con successo"
    success_url = reverse_lazy('users:profile')
