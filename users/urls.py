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
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update-user/', UserUpdateView.as_view(), name='update_user'),
    path('profile/delete-user', UserDeleteView.as_view(), name='delete_user'),
]
