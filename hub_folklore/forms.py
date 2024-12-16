import datetime

from django import forms
from django.core.validators import RegexValidator

from eventi.models import Evento

alphanumeric = RegexValidator(r'^[a-zA-Z ]*$', 'Sono consentiti solamente caratteri dell\'alfabeto e spazi.')


class SearchForm(forms.Form):
    search_query = forms.CharField(label='Testo da cercare', max_length=100, min_length=3, required=False, validators=[alphanumeric])
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

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()
        if not cleaned_data.get('search_from_data'):
            cleaned_data['search_from_data'] = datetime.date.today()
        elif cleaned_data.get('search_from_data') < datetime.date.today():
            self.add_error("search_from_data", "La data inserita è precedente alla data di oggi")
        return cleaned_data
