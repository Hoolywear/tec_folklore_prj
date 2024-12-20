from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth.models import User, Group
from django.core.mail import mail_admins, send_mail
from django.forms import ModelForm, CharField, EmailField, URLField, TextInput, forms

from eventi.models import Prenotazione, AttesaEvento
from promozioni.models import Promotore


class RegisterForm(UserCreationForm):

    email = EmailField(required=True)

    helper = FormHelper()
    helper.form_id = 'register_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Registrati'))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name='Visitatori')
        user.groups.add(g)

        send_mail(
            "Utente creato su Hub Folklore 3.0",
            f"Benvenuto in Hub Folklore 3.0! Con questa mail ti confermiamo l'avvenuta creazione dell'account.",
            "account@hubfolklore.it",
            [user.email],
        )
        return user


class LoginForm(AuthenticationForm):

    helper = FormHelper()
    helper.form_id = 'login_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Login'))

    class Meta:
        model = User
        fields = ['username', 'password']


class UserPasswordResetForm(PasswordResetForm):
    helper = FormHelper()
    helper.form_id = 'password_reset_form'
    helper.add_input(Submit('submit', 'Invia link'))


class UserPasswordResetConfirmForm(SetPasswordForm):
    helper = FormHelper()
    helper.form_id = 'password_reset_confirm_form'
    helper.add_input(Submit('submit', 'Conferma'))


class UserUpdateForm(ModelForm):
    helper = FormHelper()
    helper.form_id = 'user_update_form'
    helper.add_input(Submit('submit', 'Aggiorna'))

    class Meta:
        model = User
        fields = ['username', 'email']


class UserDeleteForm(forms.Form):
    username = CharField(required=True, label="Inserisci il tuo nome utente per confermare questa azione",
                         widget=TextInput(attrs={'placeholder': 'Il tuo username'}))


class UserChangePasswordForm(PasswordChangeForm):
    helper = FormHelper()
    helper.form_id = 'user_password_change_form'
    helper.add_input(Submit('submit', 'Cambia la password'))


class DeletePrenotazioneForm(ModelForm):

    class Meta:
        model = Prenotazione
        fields = []


class PromotoreRegisterForm(UserCreationForm):
    first_name = CharField(required=True, label='Nome')
    last_name = CharField(required=True, label='Cognome')
    email = EmailField(required=True, label='Email')
    website_field = URLField(required=True, label='Sito Web')

    helper = FormHelper()
    helper.form_id = 'promotore_register_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Richiedi registrazione'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

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
