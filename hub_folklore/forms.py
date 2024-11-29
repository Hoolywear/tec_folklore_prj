import datetime

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError

from eventi.models import Evento


class SearchForm(forms.Form):
    search_query = forms.CharField(label='Testo da cercare', max_length=100, min_length=3, required=False)
    search_from_data = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            },
        ),
        required=False,
        initial=datetime.date.today(),
        label='Eventi dal',
    )
    search_categoria = forms.ChoiceField(
        label='Categoria',
        choices=(('all', 'Tutti gli eventi'),) + Evento.CATEGORY_CHOICES,
        required=False
    )

    helper = FormHelper()
    helper.form_id = 'search_crispy_form'
    helper.form_action = 'search'
    helper.add_input(Submit('submit', 'Cerca'))

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()
        if not cleaned_data.get('search_from_data'):
            cleaned_data['search_from_data'] = datetime.date.today()
        elif cleaned_data.get('search_from_data') < datetime.date.today():
            # TODO : verificare una volta aggiunto lo styling quale va meglio
            self.add_error("search_from_data", "La data inserita è precedente alla data di oggi")
            # raise ValidationError("La data inserita è precedente alla data di oggi")
        return cleaned_data
