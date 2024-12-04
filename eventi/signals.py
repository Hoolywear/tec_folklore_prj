from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import pluralize

from eventi.models import Prenotazione, AttesaEvento


@receiver(post_save, sender=Prenotazione)
def send_event_booking_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            "Hai prenotato un evento!",
            f"Hai prenotato {instance.posti} {pluralize(instance.posti, 'posto,posti')} per {instance.evento}.",
            "eventi@hubfolklore.it",
            [instance.utente.email]
        )


@receiver(post_save, sender=AttesaEvento)
def send_waitlist_subscription_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            "Ti sei iscritto alla lista d'attesa!",
            f"Ti sei iscritto alla lista d'attesa per {instance.evento}.",
            "waitlist@hubfolklore.it",
            [instance.utente.email]
        )
