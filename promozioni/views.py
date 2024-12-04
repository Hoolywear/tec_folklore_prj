from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from braces.views import GroupRequiredMixin

from authutils import PromotoreRequiredMixin, user_passes_test_403, is_promotore
from promozioni.forms import UpdatePromoForm, DeletePromoForm
from promozioni.models import Promozione


# Create your views here.


class ListaPromoView(LoginRequiredMixin, PromotoreRequiredMixin, ListView):
    model = Promozione
    template_name = 'promozioni/lista_promozioni.html'

    def get_queryset(self):
        return Promozione.objects.filter(promotore=self.request.user.promotore)


@login_required
@user_passes_test_403(is_promotore)
def add_promo(request):
    form = UpdatePromoForm()
    if request.method == 'POST':
        form = UpdatePromoForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.promotore = request.user.promotore
            form.save()
            messages.success(request, 'Promozione aggiunta correttamente!')
            return redirect('users:promozioni:lista_promozioni')
    return render(request, template_name='promozioni/operazioni_promo.html',
                  context={'form': form, 'promo_op_titolo': 'Aggiungi promozione'})


class PromozioneView(LoginRequiredMixin, PromotoreRequiredMixin, SingleObjectMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    model = Promozione
    template_name = 'promozioni/operazioni_promo.html'

    def test_func(self):
        # controlla che la Promozione sia stata creata dall'utente
        return self.request.user.promotore == self.get_object().promotore


class UpdatePromoView(PromozioneView, UpdateView):
    form_class = UpdatePromoForm
    success_url = reverse_lazy('users:promozioni:lista_promozioni')
    success_message = 'Promozione modificata con successo!'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['promo_op_titolo'] = "Modifica promozione"
        return ctx


class DeletePromoView(PromozioneView, DeleteView):
    form_class = DeletePromoForm
    success_url = reverse_lazy('users:promozioni:lista_promozioni')
    success_message = 'Promozione eliminata con successo!'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['promo_op_titolo'] = "Elimina promozione"
        ctx['promo_op_descrizione'] = "Sei sicuro di voler eliminare questa promozione?"
        return ctx
