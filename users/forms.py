from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.core.mail import mail_admins, send_mail
from django.forms import ModelForm, CharField, EmailField, URLField

from eventi.models import Prenotazione, AttesaEvento
from promozioni.models import Promotore


class RegisterForm(UserCreationForm):

    helper = FormHelper()
    helper.form_id = 'register_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Registrati'))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):

    helper = FormHelper()
    helper.form_id = 'login_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Login'))

    class Meta:
        model = User
        fields = ['username', 'password']


class UserUpdateForm(ModelForm):
    helper = FormHelper()
    helper.form_id = 'user_update_form'
    helper.add_input(Submit('submit', 'Aggiorna'))

    class Meta:
        model = User
        fields = ['username', 'email']


class UserDeleteForm(ModelForm):
    helper = FormHelper()
    helper.form_id = 'user_delete_form'
    helper.add_input(Submit('submit', 'Elimina utente'))

    class Meta:
        model = User
        fields = []


class UserChangePasswordForm(PasswordChangeForm):
    helper = FormHelper()
    helper.form_id = 'user_password_change_form'
    helper.add_input(Submit('submit', 'Cambia la password'))


class DeletePrenotazioneForm(ModelForm):
    helper = FormHelper()
    helper.form_id = 'delete_prenotazione_form'
    helper.add_input(Submit('submit', 'Elimina prenotazione'))

    class Meta:
        model = Prenotazione
        fields = []


class DeleteAttesaForm(ModelForm):
    helper = FormHelper()
    helper.form_id = 'delete_attesa_form'
    helper.add_input(Submit('submit', 'Esci dalla waitlist'))

    class Meta:
        model = AttesaEvento
        fields = []


class PromotoreRegisterForm(RegisterForm):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = EmailField(required=True)
    website_field = URLField(required=True, label='Sito Web')

    def save(self, commit=True):
        website = self.cleaned_data['website_field']
        # creo il nuovo utente e lo aggiungo al gruppo Promotori
        user = super().save(commit)
        g = Group.objects.get(name='Promotori')
        user.groups.add(g)
        # creo il profilo promotore con l'indirizzo web inserito nel form
        promo_profile = Promotore()
        promo_profile.user = user
        promo_profile.website_field = website
        promo_profile.save()
        # disattivo l'account e invio una email agli amministratori, che eventualmente valideranno la richiesta
        # attivando l'account del promotore
        user.is_active = False
        user.save()
        mail_admins(
            "Richiesta iscrizione promotore",
            f"Nuova richiesta di iscrizione come promotore da parte di {user.first_name} {user.last_name}.\n"
            f"Per approvarla, attiva l'account con username {user.username}.",
            fail_silently=False,
        )
        # invia una mail al richiedente
        send_mail(
            "Richiesta di iscrizione in attesa",
            f"La tua richiesta di iscrizione a Hub Folklore 3.0 come {user.username} è in attesa di approvazione!\n"
            f"Riceverai una email di conferma di attivazione a breve.",
            "admin@hubfolklore.it",
            [user.email],
        )
        return user
