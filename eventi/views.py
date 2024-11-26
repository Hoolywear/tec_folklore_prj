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
        ctx['titolo'] = "Tutti gli eventi registrati"
        return ctx

    def get_queryset(self):
        return Evento.objects.filter(data_ora__gte=datetime.datetime.today()).order_by('data_ora')


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

    # scarta gli eventi passati e ordinali per data crescente, per poterli mostrare a fine pagina
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        print(self.kwargs['pk'])
        print(self.object)
        ctx['eventi'] = self.object.eventi.filter(data_ora__gte=datetime.datetime.today()).order_by('data_ora')
        return ctx


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
        from_d = datetime.datetime.strptime(self.request.resolver_match.kwargs["from_d"], '%Y-%m-%d')
        categoria = self.request.resolver_match.kwargs['categoria']
        print(from_d, categoria)
        if categoria != 'all':
            qs = qs.filter(categoria=categoria)
        return qs.filter(data_ora__gte=from_d)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cat = self.request.resolver_match.kwargs['categoria']
        if cat == 'all':
            ctx['categoria'] = 'Tutti gli eventi'
        else:
            ctx['categoria'] = dict(Evento.CATEGORY_CHOICES)[cat]
        ctx['titolo'] = f"{ctx['categoria']} dal {self.request.resolver_match.kwargs['from_d']}"
        return ctx


class ListaEventiRisultatiQueryView(ListaEventiRisultatiView):
    def get_queryset(self):
        q = self.request.resolver_match.kwargs["q"]
        return super().get_queryset().filter(Q(titolo__icontains=q) | Q(descrizione__icontains=q))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] += f" che corrispondono a '{self.request.resolver_match.kwargs['q']}'"
        return ctx
