from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from .imgutils import *


# Create your models here.

class Luogo(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField()
    indirizzo = models.CharField(max_length=150)
    sito_web = models.URLField()
    thumbnail = models.ImageField(upload_to=save_rename_luogo_img, default=None)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = 'Luoghi'


class Evento(models.Model):
    CATEGORY_CHOICES = (
        ('laboratorio', 'Laboratori e corsi'),
        ('concerto', 'Concerti'),
        ('spettacolo', "Spettacoli ed eventi teatrali"),
        ('mostra', 'Mostre e installazioni'),
        ('conferenza', 'Conferenze e convegni'),
        ('fiera', 'Fiere, sagre, mercatini, festival'),
        ('live', 'Altri eventi dal vivo')
    )

    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    posti = models.IntegerField(default=10)
    data_ora = models.DateTimeField()
    categoria = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='live')
    tags = TaggableManager(blank=True)
    luogo = models.ForeignKey(Luogo, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventi')
    thumbnail = models.ImageField(upload_to=save_rename_evento_img, default=None)
    interessi = models.ManyToManyField(User, related_name='interessi')

    def posti_disponibili(self):
        posti_prenotati = 0
        for p in self.prenotazioni.all():
            posti_prenotati += p.posti

        return self.posti - posti_prenotati

    def evento_pieno(self):
        return self.posti_disponibili() == 0

    def evento_avvenuto(self):
        return self.data_ora < timezone.now()

    def interessi_count(self):
        return self.interessi.count()

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name_plural = 'Eventi'


class Prenotazione(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='prenotazioni')
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prenotazioni')
    posti = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Prenotazioni'
        constraints = [
            models.UniqueConstraint(fields=['evento', 'utente'], name='unique_prenotazione')
        ]

    def __str__(self):
        return str(f'Prenotazione per {self.evento.titolo} (posti: {self.posti})')


class AttesaEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='attese')
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attese')

    class Meta:
        verbose_name_plural = 'Attese Evento'
        constraints = [
            models.UniqueConstraint(fields=['evento', 'utente'], name='unique_attese'),
        ]

    def __str__(self):
        return str(f'Attesa per {self.evento.titolo}')
