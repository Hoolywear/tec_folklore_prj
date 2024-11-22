from django import forms


class SearchForm(forms.Form):
    search_query = forms.CharField(label='Testo da cercare', max_length=100, min_length=3, required=True)
