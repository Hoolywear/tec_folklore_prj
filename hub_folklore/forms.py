import datetime

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, Field


class SearchForm(forms.Form):
    search_query = forms.CharField(label='Testo da cercare', max_length=100, min_length=3, required=True)
    search_min_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        initial=datetime.date.today(),
        label='Data da cercare'
    )
    helper = FormHelper()
    helper.form_id = 'search_crispy_form'
    helper.form_action = 'search'
    helper.add_input(Submit('submit', 'Cerca'))
