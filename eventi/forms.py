import datetime

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.template.defaultfilters import pluralize

from eventi.models import Prenotazione, Evento


class PrenotaEventoForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'prenota_evento_form'
    helper.add_input(Submit('submit', 'Prenota'))

    class Meta:
        model = Prenotazione
        fields = ['posti']

    def custom_is_valid(self, evento):
        if self.is_valid():
            cleaned_data = self.cleaned_data
            posti = cleaned_data.get('posti')
            disp = evento.posti_disponibili()
            if posti > disp:
                self.add_error('posti', ValidationError(
                    f"L'evento ha ancora solo {disp} post{pluralize(disp, 'o,i')} disponibil{pluralize(disp, 'e,i')}"))
        return self.is_valid()
