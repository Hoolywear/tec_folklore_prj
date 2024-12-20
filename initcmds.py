import datetime
import json
import os

from django.utils.timezone import make_aware

from eventi.models import *
from hub_folklore.settings import MEDIA_ROOT

from PIL import Image


# Funzioni per il popolamento del database con dati fittizi

def get_info():
    return (f'DATI ATTUALI: {Luogo.objects.all().count()} luoghi, {Evento.objects.all().count()} eventi, '
            f'{Prenotazione.objects.all().count()} prenotazioni, {AttesaEvento.objects.all().count()} attese')


def erase_db():
    print("DATI PRE-RIMOZIONE: ", get_info())
    print("Cancello il DB")
    Evento.objects.all().delete()
    Luogo.objects.all().delete()
    Prenotazione.objects.all().delete()
    AttesaEvento.objects.all().delete()
    print("DB cancellato")
    print(get_info())


def init_db():
    if len(Evento.objects.all()) != 0:
        print("NESSUN RIPOPOLAMENTO -", get_info())
        return

    # importazione fixtures da file
    try:
        fixture_luoghi = open('fixtures/luoghi.json', 'r')
        fixture_eventi = open('fixtures/eventi.json', 'r')
        # carica tramite modulo python (genera strutture dati appropriate)
        luoghi = json.load(fixture_luoghi)
        eventi = json.load(fixture_eventi)

        fixture_luoghi.close()
        fixture_eventi.close()
    except OSError as e:
        print("Errore nell'importazione delle fixture! Interrompo il popolamento...", e)
        return

    print("Inizio il popolamento...")

    for luogo in luoghi:
        new_luogo = Luogo()
        new_luogo.nome = luogo['nome']
        new_luogo.descrizione = luogo['descrizione']
        new_luogo.indirizzo = luogo['indirizzo']
        new_luogo.image = 'imgs/def_imgs/' + luogo['image']
        new_luogo.sito_web = luogo['sito_web']
        new_luogo.save()

    for evento in eventi:
        new_evento = Evento()
        new_evento.titolo = evento['titolo']
        new_evento.descrizione = evento['descrizione']
        new_evento.posti = evento['posti']
        # converto dal formato di data_ora in fixtures/eventi.json:
        data_ora = datetime.strptime(evento['data_ora'], '%Y-%m-%dT%H:%M:%SZ')
        # da https://stackoverflow.com/questions/18622007/runtimewarning-datetimefield-received-a-naive-datetime
        # per risolvere "RuntimeWarning: DateTimeField received a naive datetime" (dovuto alla formattazione del
        # campo data_ora in fixture/eventi.json)
        new_evento.data_ora = data_ora
        new_evento.luogo = Luogo.objects.get(nome__exact=evento['luogo'])
        new_evento.categoria = evento['categoria']
        new_evento.image = 'imgs/def_imgs/' + evento['image']
        new_evento.save()
        new_evento = Evento.objects.get(titolo__exact=evento['titolo'])
        for tag in evento['tag']:
            new_evento.tags.add(tag)
        new_evento.save()

    print("POPOLAMENTO ESEGUITO CON SUCCESSO!", get_info())
