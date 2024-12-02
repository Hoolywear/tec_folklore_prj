from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin

from promozioni.forms import UpdatePromoForm, DeletePromoForm
from promozioni.models import Promozione


# Create your views here.
def is_promotore(user):
    return user.groups.filter(name='Promotori').exists()


class ListaPromoView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Promozione
    template_name = 'promozioni/lista_promozioni.html'

    def get_queryset(self):
        return Promozione.objects.filter(promotore=self.request.user.promotore)

    def test_func(self):
        # controlla che l'utente sia Promotore
        return is_promotore(self.request.user)


@login_required
@user_passes_test(is_promotore)
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


class PromozioneView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, SingleObjectMixin, View):
    model = Promozione
    template_name = 'promozioni/operazioni_promo.html'

    def test_func(self):
        # controlla che l'utente sia Promotore
        t1 = is_promotore(self.request.user)
        # controlla che la Promozione sia stata creata dall'utente
        t2 = self.request.user.promotore == self.get_object().promotore
        return t1 and t2


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
