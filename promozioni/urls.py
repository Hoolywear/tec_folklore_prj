from django.urls import path

from promozioni.views import ListaPromoView, UpdatePromoView, DeletePromoView, add_promo

app_name = 'promozioni'

urlpatterns = [
    path('', ListaPromoView.as_view(), name='lista_promozioni'),
    path('add/', add_promo, name='aggiungi_promozione'),
    path('<int:pk>/update/', UpdatePromoView.as_view(), name='modifica_promozione'),
    path('<int:pk>/delete/', DeletePromoView.as_view(), name='elimina_promozione'),
]
