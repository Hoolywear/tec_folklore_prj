from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from authutils import VisitatoreRequiredMixin, is_visitatore, user_passes_test_403
from eventi.models import Evento
from .forms import *


# Create your views here.


'''
GENERIC AUTH VIEWS
'''


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


class PromotoreRegisterView(RegisterView):
    form_class = PromotoreRegisterForm
    success_message = "Richiesta di iscrizione inviata! Attendi l'approvazione dello staff"
    success_url = reverse_lazy('index')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logout eseguito con successo!")
    return redirect('index')


'''
GENERIC PROFILE VIEWS
'''


@login_required
def profile(request):
    # se admin, manda direttamente alla dashboard admin
    if request.user.is_staff:
        return redirect('admin:index')
    return render(request, 'users/profile.html')


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = "Il profilo è stato aggiornato correttamente"
    template_name = 'users/manage/update_user.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, *args):  # riconosco l'utente loggato
        return self.request.user


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    form_class = UserDeleteForm
    success_message = "L'account è stato eliminato correttamente"
    template_name = 'users/manage/delete_user.html'
    success_url = reverse_lazy('users:register')

    def get_object(self, *args):
        return self.request.user


class UserChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/manage/change_password.html'
    form_class = UserChangePasswordForm
    success_message = "Password cambiata con successo"
    success_url = reverse_lazy('users:profile')


'''
VISITATORI VIEWS
'''


class ListaUserItemsView(LoginRequiredMixin, VisitatoreRequiredMixin, ListView):

    def get_queryset(self):
        return self.model.objects.filter(utente=self.request.user)


class ListaPrenotazioniView(ListaUserItemsView):
    model = Prenotazione
    template_name = 'users/lista_prenotazioni.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['prenotazioni_attive'] = self.object_list.filter(evento__in=Evento.active_objects.all())
        print(ctx['prenotazioni_attive'])
        ctx['prenotazioni_passate'] = self.object_list.exclude(evento__in=Evento.active_objects.all())
        print(ctx['prenotazioni_passate'])
        return ctx


@login_required
@user_passes_test_403(is_visitatore)
def delete_prenotazione(request, pk):
    p = get_object_or_404(Prenotazione, pk=pk)

    if request.user != p.utente:
        raise PermissionDenied

    if not p.evento.evento_attivo():
        messages.error(request, "Non puoi eliminare una prenotazione una volta passata la data dell'evento")
        return redirect('users:prenotazioni')

    if request.method == 'POST':
        form = DeletePrenotazioneForm(request.POST)
        if form.is_valid():
            p.delete()
            messages.success(request, "Prenotazione eliminata con successo!")
            return redirect('users:prenotazioni')
    form = DeletePrenotazioneForm()
    ctx = {
        'form': form,
        'object': p,
        'titolo': f"Elimina prenotazione per {p.evento}",
        'descrizione': f"Sei sicuro di voler eliminare la prenotazione per {p.evento}?",
        'back_url': reverse('users:prenotazioni')
    }
    return render(request, 'users/delete_user_item.html', ctx)


class ListaAtteseView(ListaUserItemsView):
    model = AttesaEvento
    template_name = 'users/lista_attese.html'

    def get_queryset(self):
        qs = super().get_queryset()

        for attesa in qs:
            if not attesa.evento.evento_attivo():
                attesa.delete()
        return qs


class DeleteAttesaView(LoginRequiredMixin, VisitatoreRequiredMixin, SuccessMessageMixin, DeleteView):
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


@login_required
@user_passes_test_403(is_visitatore)
def lista_interessi(request):
    interessi = request.user.interessi.all()
    return render(request, 'users/lista_interessi.html', {'interessi': interessi})
