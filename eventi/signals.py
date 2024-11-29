from django.core.mail import send_mail
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from eventi.models import Prenotazione, Evento


@receiver(pre_delete, sender=Prenotazione)
def send_waitlist_emails(sender, instance, **kwargs):
    try:
        evento = Evento.objects.get(pk=instance.evento.pk)
        if evento.evento_pieno():
            waitlist = [attesa.utente.email for attesa in evento.attese.all()]
            print("Sending emails to waitlist members...")
            send_mail(
                "Si sono liberati dei posti!",
                f"Si sono liberati dei posti per l'evento {evento}, affrettati a prenotarlo!",
                "waitlist@hubfolklore.it",
                waitlist
            )
    except Evento.DoesNotExist:
        print("error")
