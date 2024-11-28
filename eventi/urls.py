"""
URL configuration for hub_folklore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from .views import *

app_name = 'eventi'

urlpatterns = [
    path('', ListaEventiView.as_view(), name='eventi'),
    path('tag/<str:tag>', ListaEventiTagView.as_view(), name='eventi_tag'),
    path("search/<str:from_d>/<str:categoria>/", ListaEventiRisultatiView.as_view(), name='risultati_ricerca'),
    path("search/<str:from_d>/<str:categoria>/<str:q>/", ListaEventiRisultatiQueryView.as_view(), name='risultati_ricerca_q'),
    path('dettagli/<int:pk>/', DettagliEventoView.as_view(), name='dettagli_evento'),
    path('luoghi/', ListaLuoghiView.as_view(), name='luoghi'),
    path('luoghi/dettagli/<int:pk>/', DettagliLuogoView.as_view(), name='dettagli_luogo'),
    path('<int:pk>/prenota/', prenota_evento, name='prenota_evento'),
]
