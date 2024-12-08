import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from authutils import is_promotore
from eventi.models import Prenotazione
from promozioni.models import Promozione
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
            from_d = datetime.datetime.strftime(form.cleaned_data.get('search_from_data'), "%Y-%m-%d")
            categoria = form.cleaned_data.get('search_categoria')
            if q:
                return redirect("eventi:risultati_ricerca_q", from_d, categoria, q)
            return redirect("eventi:risultati_ricerca", from_d, categoria)
    else:
        form = SearchForm()
    return render(request, template_name='search.html', context={'form': form})


def admin_stats(request):
    if not request.user.is_staff:
        raise PermissionDenied("Richiesti permessi di amministratore")
    ctx = {
        'utenti': User.objects.all().count(),
        'prenotazioni': Prenotazione.objects.all().count(),
        'attese': Prenotazione.objects.all().count(),
    }
    promozioni = Promozione.objects.all()
    visite_anonime = 0
    visite_registrate = 0
    for promo in promozioni:
        visite_anonime += promo.visite_anonime
        visite_registrate += promo.visite_registrate
    ctx['promozioni'] = promozioni.count()
    ctx['visite_anonime'] = visite_anonime
    ctx['visite_registrate'] = visite_registrate
    return render(request, 'admin_stats.html', ctx)


def random_promo(request):
    ctx = {'promo': random.choice(Promozione.objects.all())}
    return render(request, 'promo_landing.html', ctx)


def promo_click(request, pk):
    if is_promotore(request.user):
        messages.error(request, "Un promotore non può contribuire alle statistiche delle inserzioni")
    else:
        promo = get_object_or_404(Promozione, pk=pk)
        if request.user.is_authenticated:
            promo.visite_registrate += 1
            promo.save()
        else:
            promo.visite_anonime += 1
            promo.save()
        messages.success(request, "Hai cliccato su un link promozionale e sei stato redirezionato fuori\
         dalla piattaforma")
    return redirect('index')
