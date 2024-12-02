from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from promozioni.models import Promotore, Promozione

# Register your models here.


# da docs.djangoproject.com per inserire la sezione custom in fondo ai profili utente sulla pagina admin
class PromotoreInline(admin.StackedInline):
    model = Promotore
    can_delete = False
    verbose_name_plural = "promotori"


class UserAdmin(BaseUserAdmin):
    inlines = [PromotoreInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Promozione)
