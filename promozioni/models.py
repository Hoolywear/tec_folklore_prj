from django.contrib.auth.models import User
from django.db import models
from taggit.models import Tag


# Create your models here.

class Promotore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    homepage = models.URLField(blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Promotori'


class Promozione(models.Model):
    utente = models.ForeignKey(Promotore, on_delete=models.CASCADE)
    banner = models.ImageField(upload_to='promozione/%Y/%m/%d')
    website = models.URLField()
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'Inserzione di {self.utente} con tag {self.tags.all()}'

    class Meta:
        verbose_name_plural = 'Promozioni'
