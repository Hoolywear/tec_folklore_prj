import datetime
import json
from eventi.models import *


# Funzioni per il popolamento del database con dati fittizi

def erase_db():
    print("Cancello il DB")
    Luogo.objects.all().delete()
    Evento.objects.all().delete()


def init_db():
    if len(Evento.objects.all()) != 0:
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

    for luogo in luoghi:
        new_luogo = Luogo()
        new_luogo.nome = luogo['nome']
        new_luogo.descrizione = luogo['descrizione']
        new_luogo.indirizzo = luogo['indirizzo']
        new_luogo.sito_web = luogo['sito_web']
        new_luogo.save()

    for evento in eventi:
        new_evento = Evento()
        new_evento.titolo = evento['titolo']
        new_evento.descrizione = evento['descrizione']
        new_evento.posti = evento['posti']
        new_evento.data_ora = datetime.datetime.strptime(evento['data_ora'], '%Y-%m-%dT%H:%M:%SZ')
        new_evento.luogo = Luogo.objects.get(nome__exact=evento['luogo'])
        new_evento.save()
        new_evento = Evento.objects.get(titolo__exact=evento['titolo'])
        for tag in evento['tag']:
            new_evento.tags.add(tag)
        new_evento.save()

    print("DUMP DB")
    print(Luogo.objects.all())
    print(Evento.objects.all())
    print(f'Caricati {Luogo.objects.all().count()} luoghi e {Evento.objects.all().count()} eventi')
