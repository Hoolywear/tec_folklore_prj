import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView

from authutils import user_passes_test_403, is_visitatore
from eventi.forms import PrenotaEventoForm
from eventi.models import *


class ListaEventiView(ListView):
    model = Evento
    template_name = 'eventi/lista_risultati.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titolo'] = "Tutti gli eventi registrati"
        return ctx

    def get_queryset(self):
        # non mostro gli eventi passati
        return Evento.active_objects.order_by('data_ora')


class DettagliEventoView(DetailView):
    model = Evento
    template_name = 'eventi/dettagli_evento.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        interessi = self.object.interessi
        interessato = False
        if interessi.filter(id=self.request.user.id).exists():
            interessato = True
        ctx['interessati'] = self.object.interessi_count()
        ctx['interessato'] = interessato

        return ctx


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
        ctx['eventi'] = self.object.eventi.filter(data_ora__gte=datetime.today()).order_by('data_ora')
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
        from_d = datetime.strptime(self.request.resolver_match.kwargs["from_d"], '%Y-%m-%d')
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


@login_required
@user_passes_test_403(is_visitatore)
def prenota_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if not evento.evento_attivo():
        messages.error(request, "L'evento è passato!")
        return redirect('eventi:eventi')

    if evento.evento_pieno():
        messages.error(request, "L'evento è esaurito!")
        return redirect('eventi:dettagli_evento', pk=pk)

    try:
        Prenotazione.objects.get(evento=evento, utente=request.user)
        messages.error(request, "Hai già una prenotazione per l'evento!")
        return redirect('eventi:dettagli_evento', pk=pk)
    except Prenotazione.DoesNotExist:
        if request.method == 'POST':
            form = PrenotaEventoForm(request.POST)
            if form.custom_is_valid(evento):
                form.instance.utente = request.user
                form.instance.evento = evento
                try:
                    form.save()
                except IntegrityError:
                    messages.error(request, "Hai già una prenotazione per questo evento!")
                    return redirect('eventi:dettagli_evento', pk=pk)
                try:
                    at = AttesaEvento.objects.get(evento=evento, utente=request.user)
                    at.delete()
                    messages.success(request, "La tua attesa per l'evento è stata rimossa.")
                except AttesaEvento.DoesNotExist:
                    print("L'utente non è in lista d'attesa. Non sono state rimosse Attese.")
                messages.success(request, "Evento prenotato! Gestiscilo dal tuo profilo")
                return redirect("eventi:dettagli_evento", pk=pk)
        else:
            form = PrenotaEventoForm()
        return render(request, template_name='eventi/prenota_evento.html', context={'form': form, 'ev': evento})


@login_required
@user_passes_test_403(is_visitatore)
def attesa_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if not evento.evento_attivo():
        messages.error(request, "L'evento è passato!")
        return redirect('eventi:eventi')

    if not evento.evento_pieno():
        messages.error(request, "L'evento ha ancora posti disponibili")
        return redirect('eventi:dettagli_evento', pk=pk)
    try:
        Prenotazione.objects.get(evento=evento, utente=request.user)
        messages.error(request, "Hai già una prenotazione per l'evento!")
    except Prenotazione.DoesNotExist:
        try:
            attesa = AttesaEvento(evento=evento, utente=request.user)
            attesa.save()
            messages.success(request, "Sei in lista di attesa!")
        except IntegrityError as e:
            messages.error(request, "Sei già in lista di attesa!")
    return redirect("eventi:dettagli_evento", pk=pk)


@login_required()
@user_passes_test_403(is_visitatore)
def interesse_evento(request, pk):
    evento = get_object_or_404(Evento, pk=request.POST.get('evento_pk'))

    if evento.interessi.filter(id=request.user.id).exists():
        evento.interessi.remove(request.user)
        messages.success(request, "Interesse rimosso")
    else:
        if evento.evento_attivo():
            evento.interessi.add(request.user)
            messages.success(request, "Interesse aggiunto!")
        else:
            messages.error(request, "Impossibile mostrare interesse! Evento passato")

    return redirect('eventi:dettagli_evento', pk)
