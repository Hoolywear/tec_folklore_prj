from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


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
