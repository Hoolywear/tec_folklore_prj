from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from eventi.models import Prenotazione


class RegisterForm(UserCreationForm):

    helper = FormHelper()
    helper.form_id = 'register_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Register'))

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
