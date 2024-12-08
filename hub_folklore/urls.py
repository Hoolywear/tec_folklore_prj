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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from initcmds import *
from .views import *
from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-stats/', admin_stats, name='admin_stats'),
    re_path(r"^$|^/$|^home/$|^index/$", index, name='index'),
    path('search/', search, name='search'),
    path('about/', about, name='about'),
    path('altre-promo/', random_promo, name='random_promo'),
    path('altre-promo/<int:pk>/', promo_click, name='promo_click'),
    path('eventi/', include('eventi.urls')),
    path('users/', include('users.urls')),
]
if DEBUG:  # new
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)


# erase_db()
init_db()
