from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from promozioni.models import Promozione


class UpdatePromoForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'update_promo_form'
    helper.add_input(Submit('submit', 'Salva', css_class='btn btn-primary w-100'))

    class Meta:
        model = Promozione
        fields = ['website', 'banner', 'tags']


class DeletePromoForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'delete_promo_form'
    helper.add_input(Submit('submit', 'Elimina'))

    class Meta:
        model = Promozione
        fields = []
