from django.shortcuts import render, redirect
from .forms import *


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data.get('search_query')
            min_date = form.cleaned_data.get('search_min_date')
            return redirect("eventi:risultati_ricerca", q, min_date)
    else:
        form = SearchForm()
    return render(request, template_name='search.html', context={'form': form})