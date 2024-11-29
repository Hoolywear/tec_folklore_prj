import profile

from django.contrib import admin
from django.urls import path
from .views import *
from initcmds import *
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update-user/', UserUpdateView.as_view(), name='update_user'),
    path('profile/delete-user', UserDeleteView.as_view(), name='delete_user'),
    path('profile/change-password/', UserChangePasswordView.as_view(), name='change_password'),
    path('profile/prenotazioni/', ListaPrenotazioniView.as_view(), name='prenotazioni'),
    path('profile/prenotazioni/<int:pk>/delete/', DeletePrenotazioneView.as_view(), name='delete_prenotazione'),
    path('profile/waitlist/', ListaAtteseView.as_view(), name='waitlist'),
    path('profile/waitlist/<int:pk>/delete/', DeleteAttesaView.as_view(), name='delete_attesa'),
]
