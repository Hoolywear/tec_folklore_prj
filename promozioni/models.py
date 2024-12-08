from django.contrib.auth.models import User
from django.db import models
from taggit.models import Tag


# Create your models here.

class Promotore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='promotore')
    homepage = models.URLField(blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Promotori'


class Promozione(models.Model):
    promotore = models.ForeignKey(Promotore, on_delete=models.CASCADE)
    banner = models.ImageField(upload_to='promozioni/banners/')
    website = models.URLField(unique=True)
    tags = models.ManyToManyField(Tag, blank=True)
    visite_anonime = models.IntegerField(default=0)
    visite_registrate = models.IntegerField(default=0)

    def __str__(self):
        return f'Inserzione di {self.promotore} con tag {self.tags.all()}'


    class Meta:
        verbose_name_plural = 'Promozioni'
