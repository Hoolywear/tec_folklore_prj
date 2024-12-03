from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include

from .views import *

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/manage/password_reset_confirm.html',
                                          form_class=UserPasswordResetConfirmForm,
                                          success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='users/manage/password_reset_complete.html'),
         name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update-user/', UserUpdateView.as_view(), name='update_user'),
    path('profile/delete-user', UserDeleteView.as_view(), name='delete_user'),
    path('profile/change-password/', UserChangePasswordView.as_view(), name='change_password'),
    path('profile/prenotazioni/', ListaPrenotazioniView.as_view(), name='prenotazioni'),
    path('profile/prenotazioni/<int:pk>/delete/', DeletePrenotazioneView.as_view(), name='delete_prenotazione'),
    path('profile/waitlist/', ListaAtteseView.as_view(), name='waitlist'),
    path('profile/waitlist/<int:pk>/delete/', DeleteAttesaView.as_view(), name='delete_attesa'),
    path('profile/interessi/', lista_interessi, name='interessi'),
    path('promo/', include('promozioni.urls')),
    path('register-promotore/', PromotoreRegisterView.as_view(), name='register_promotore'),
]
