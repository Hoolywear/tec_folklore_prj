from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import pluralize

from eventi.models import Prenotazione


class PrenotaEventoForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'prenota_evento_form'
    helper.add_input(Submit('submit', 'Prenota'))

    class Meta:
        model = Prenotazione
        fields = ['posti']
