import datetime

from django.db.models import Q
from django.views.generic import ListView, DetailView
from eventi.models import *

# Create your views here.


class ListaEventiView(ListView):
    model = Evento
    template_name = 'eventi/lista_risultati.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] = "Eventi registrati"
        return ctx

    def get_queryset(self):
        return Evento.objects.filter(data_ora__gt=datetime.datetime.today())


class DettagliEventoView(DetailView):
    model = Evento
    template_name = 'eventi/dettagli_evento.html'


class ListaLuoghiView(ListView):
    model = Luogo
    template_name = 'eventi/lista_luoghi.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] = "Luoghi"
        return ctx


class DettagliLuogoView(DetailView):
    model = Luogo
    template_name = 'eventi/dettagli_luogo.html'


class ListaEventiTagView(ListaEventiView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(tags__name__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag'] = self.kwargs['tag']
        ctx['titolo'] = f"Eventi con tag '{ctx['tag']}'"
        return ctx


class ListaEventiRisultatiView(ListaEventiView):
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.resolver_match.kwargs["q"]
        min_date = datetime.datetime.strptime(self.request.resolver_match.kwargs["date"], '%Y-%m-%d')
        return qs.filter(Q(titolo__icontains=q) | Q(descrizione__icontains=q), Q(data_ora__gte=min_date))
