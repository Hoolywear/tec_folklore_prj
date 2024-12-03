from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from .forms import *


# Create your views here.

class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    success_message = "Utente creato correttamente!"
    template_name = "users/manage/register.html"
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        # redirect alla home se già loggato
        if request.user.is_authenticated:
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(SuccessMessageMixin, LoginView):
    authentication_form = LoginForm
    success_message = "Login avvenuto con successo!"
    template_name = "users/manage/login.html"
    redirect_authenticated_user = True


class UserPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/manage/password_reset.html'
    form_class = UserPasswordResetForm
    email_template_name = 'users/manage/password_reset_email.html'
    subject_template_name = 'users/manage/password_reset_subject.txt'
    success_message = "Ti abbiamo inviato una email con il link per resettare la password, " \
                      "se esiste un account con l'indirizzo fornito. La riceverai a breve." \
                      " Se non ricevi nessuna email, " \
                      "per favore ricontrolla l'indirizzo inserito e la cartella spam della tua casella di posta."
    success_url = reverse_lazy('index')


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/manage/password_reset_confirm.html'
    form_class = UserPasswordResetConfirmForm


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logout eseguito con successo!")
    return redirect('index')


@login_required
def profile(request):
    return render(request, 'users/profile.html')


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = "Il profilo è stato aggiornato correttamente"
    template_name = 'users/manage/update_user.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):  # riconosco l'utente loggato
        return self.request.user


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    form_class = UserDeleteForm
    success_message = "L'account è stato eliminato correttamente"
    template_name = 'users/manage/delete_user.html'
    success_url = reverse_lazy('users:register')

    def get_object(self):
        return self.request.user


class UserChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/manage/change_password.html'
    form_class = UserChangePasswordForm
    success_message = "Password cambiata con successo"
    success_url = reverse_lazy('users:profile')


class ListaUserItemsView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return self.model.objects.filter(utente=self.request.user)


class ListaPrenotazioniView(ListaUserItemsView):
    model = Prenotazione
    template_name = 'users/lista_prenotazioni.html'


class DeletePrenotazioneView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Prenotazione
    success_url = reverse_lazy('users:prenotazioni')
    template_name = 'users/delete_user_item.html'
    form_class = DeletePrenotazioneForm
    success_message = "Prenotazione eliminata con successo"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] = f"Elimina prenotazione per {self.object}"
        ctx['descrizione'] = f"Sei sicuro di voler eliminare la prenotazione per {self.object.evento}?"
        ctx['back_url'] = reverse('users:prenotazioni')
        return ctx

    def test_func(self):
        # controlla che l'utente corrisponda a quello che ha effettuato la prenotazione
        return self.request.user == self.get_object().utente


class ListaAtteseView(ListaUserItemsView):
    model = AttesaEvento
    template_name = 'users/lista_attese.html'


class DeleteAttesaView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = AttesaEvento
    success_url = reverse_lazy('users:waitlist')
    template_name = 'users/delete_user_item.html'
    form_class = DeleteAttesaForm
    success_message = "Sei stato rimosso dalla lista di attesa"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] = f"Elimina attesa per {self.object}"
        ctx['descrizione'] = f"Sei sicuro di volerti disiscrivere dalla lista di attesa per {self.object.evento}?"
        ctx['back_url'] = reverse('users:waitlist')
        return ctx

    def test_func(self):
        # controlla che l'utente corrisponda a quello che ha effettuato la prenotazione
        return self.request.user == self.get_object().utente


@login_required
def lista_interessi(request):
    interessi = request.user.interessi.all()
    return render(request, 'users/lista_interessi.html', {'interessi': interessi})


class PromotoreRegisterView(RegisterView):
    form_class = PromotoreRegisterForm
    success_message = "Richiesta di iscrizione inviata! Attendi l'approvazione dello staff"
    success_url = reverse_lazy('index')
