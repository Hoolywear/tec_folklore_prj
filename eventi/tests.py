from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse

from hub_folklore import settings
from .models import Luogo, Evento, Prenotazione, AttesaEvento
from datetime import date, datetime, timedelta


# funzione per creare oggetti datetime con time 00:00:00.0
def day_start(date_time):
    return datetime.combine(date_time.date(), datetime.min.time())


# funzione per creare un luogo di default
def create_luogo():
    return Luogo.objects.create(
            nome="Luogo prova",
            descrizione="descrizione prova",
            indirizzo="indirizzo prova",
            sito_web="https://www.prova.it"
        )


def create_evento(
        titolo="Evento prova",
        descrizione="descrizione",
        posti=None,
        data_ora=day_start(datetime.today() + timedelta(days=1)),
        categoria=None,
        luogo=create_luogo()):
    evento = Evento(
        titolo=titolo,
        descrizione=descrizione,
        data_ora=data_ora,
        luogo=luogo,
    )
    if posti:
        evento.posti = posti
    if categoria:
        evento.categoria = categoria
    evento.full_clean()
    evento.save()
    return evento


class LuogoModelTests(TestCase):

    def setUp(self):
        self.luogo = create_luogo()

    def test_luogo_creation(self):
        '''
        Controlla che tutti gli attributi siano inseriti correttamente
        '''
        self.assertEqual(self.luogo.nome, "Luogo prova")
        self.assertEqual(self.luogo.descrizione, "descrizione prova")
        self.assertEqual(self.luogo.indirizzo, "indirizzo prova")
        self.assertEqual(self.luogo.sito_web, "https://www.prova.it")

    def test_luogo_str(self):
        '''
        Controlla il metodo __str__(self)
        '''
        self.assertEqual(str(self.luogo), "Luogo prova")

    def test_luogo_default_image(self):
        '''
        Controlla che il path dell'immagine di default corrisponda a quello settato
        '''
        self.assertEqual(self.luogo.image.path, settings.MEDIA_ROOT+'/imgs/def_imgs/thumb_1.jpg')

    def test_luogo_nome_required(self):
        luogo = Luogo.objects.create(
            descrizione='prova',
            indirizzo='indirizzo prova',
            sito_web='https://www.prova.it'
        )
        with self.assertRaises(ValidationError):
            luogo.full_clean()

    def test_luogo_descrizione_required(self):
        luogo = Luogo.objects.create(
            nome='prova',
            indirizzo='indirizzo prova',
            sito_web='https://www.prova.it'
        )
        with self.assertRaises(ValidationError):
            luogo.full_clean()

    def test_luogo_indirizzo_required(self):
        luogo = Luogo.objects.create(
            nome='prova',
            descrizione='prova',
            sito_web='https://www.prova.it'
        )
        with self.assertRaises(ValidationError):
            luogo.full_clean()

    def test_luogo_sito_web_required(self):
        luogo = Luogo.objects.create(
            nome='prova',
            descrizione='prova',
            indirizzo='indirizzo prova',
        )
        with self.assertRaises(ValidationError):
            luogo.full_clean()


class EventoModelTests(TestCase):

    def setUp(self):
        self.luogo = create_luogo()
        self.evento = create_evento(
            posti=100,
            categoria='concerto',
            luogo=self.luogo
        )
        self.evento.tags.add('tag1', 'tag2')

        self.evento_required_only = create_evento(luogo=self.luogo)

    def test_evento_creation(self):
        self.assertEqual(self.evento.titolo, "Evento prova")
        self.assertEqual(self.evento.descrizione, "descrizione")
        self.assertEqual(self.evento.posti, 100)
        self.assertEqual(self.evento.data_ora, day_start(datetime.today() + timedelta(days=1)))
        self.assertEqual(self.evento.categoria, "concerto")
        self.assertEqual(self.evento.luogo, self.luogo)
        self.assertSetEqual(set(self.evento.tags.names()), {'tag1', 'tag2'})

    def test_evento_str(self):
        self.assertEqual(str(self.evento), "Evento prova")

    def test_evento_default_fields(self):
        self.assertEqual(self.evento_required_only.image.path, settings.MEDIA_ROOT+'/imgs/def_imgs/thumb_1.jpg')
        self.assertEqual(self.evento_required_only.posti, 10)
        self.assertEqual(self.evento_required_only.categoria, 'live')

    def test_evento_titolo_required(self):
        self.evento.titolo = None
        with self.assertRaises(ValidationError):
            self.evento.full_clean()

    def test_evento_descrizione_required(self):
        self.evento.descrizione = None
        with self.assertRaises(ValidationError):
            self.evento.full_clean()

    def test_evento_data_ora_required(self):
        self.evento.data_ora = None
        with self.assertRaises(ValidationError):
            self.evento.full_clean()

    def test_evento_luogo_required(self):
        self.evento.luogo = None
        with self.assertRaises(ValidationError):
            self.evento.full_clean()

    def test_evento_categoria_notin_choices(self):
        self.evento.categoria = 'categoria_sconosciuta'
        with self.assertRaises(ValidationError):
            self.evento.full_clean()

    def test_evento_posti_negativi(self):
        with self.assertRaises(IntegrityError):
            create_evento(posti=-1, luogo=self.luogo)

    def test_posti_disponibili(self):
        self.assertEqual(self.evento.posti_disponibili(), 100)
        user = User.objects.create_user(username="testuser")
        Prenotazione.objects.create(evento=self.evento, utente=user, posti=10)
        self.assertEqual(self.evento.posti_disponibili(), 90)

    def test_evento_pieno(self):
        self.assertFalse(self.evento.evento_pieno())
        user = User.objects.create_user(username="testuser")
        Prenotazione.objects.create(evento=self.evento, utente=user, posti=100)
        self.assertTrue(self.evento.evento_pieno())

    def test_evento_attivo(self):
        self.assertTrue(self.evento.evento_attivo())
        self.evento.data_ora = day_start(datetime.today() - timedelta(days=1))
        self.assertFalse(self.evento.evento_attivo())

    def test_evento_active_objects_manager(self):
        evento_passato = self.evento
        evento_passato.titolo = "Evento passato"
        evento_passato.data_ora = day_start(datetime.today() - timedelta(days=1))
        evento_passato.save()
        self.assertNotIn(evento_passato, list(Evento.active_objects.all()))

    def test_evento_interesse_count(self):
        user1 = User.objects.create(username="testuser")
        user2 = User.objects.create(username="testuser2")
        self.evento.interessi.add(user1, user2)
        self.assertEqual(self.evento.interessi_count(), 2)
        self.evento.interessi.remove(user1)
        self.assertEqual(self.evento.interessi_count(), 1)


class PrenotazioneModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.luogo = create_luogo()
        self.evento = create_evento(posti=50, luogo=self.luogo)
        self.prenotazione = Prenotazione.objects.create(
            evento=self.evento,
            utente=self.user,
            posti=5
        )

    def test_prenotazione_creation(self):
        self.assertEqual(self.prenotazione.evento, self.evento)
        self.assertEqual(self.prenotazione.utente, self.user)
        self.assertEqual(self.prenotazione.posti, 5)

    def test_prenotazione_str(self):
        self.assertEqual(str(self.prenotazione), f'Prenotazione per {self.evento.titolo} (posti: 5)')

    def test_prenotazione_unique_constraint(self):
        with self.assertRaises(Exception):
            Prenotazione.objects.create(evento=self.evento, utente=self.user, posti=5)

    def test_prenotazione_evento_required(self):
        with self.assertRaises(IntegrityError):
            Prenotazione.objects.create(
                utente=self.user,
                posti=5
            )

    def test_prenotazione_utente_required(self):
        with self.assertRaises(IntegrityError):
            Prenotazione.objects.create(
                evento=self.evento,
                posti=5
            )

    def test_prenotazione_posti_required(self):
        with self.assertRaises(IntegrityError):
            Prenotazione.objects.create(
                evento=self.evento,
                utente=User.objects.create_user(username="testuser2"),
            )

    def test_prenotazione_posti_negativi(self):
        self.prenotazione.posti = -1
        with self.assertRaises(ValidationError):
            self.prenotazione.full_clean()

    def test_prenotazione_posti_zero(self):
        self.prenotazione.posti = 0
        with self.assertRaises(ValidationError):
            self.prenotazione.full_clean()

    def test_prenotazione_posti_gte_posti_disponibili(self):
        self.prenotazione.posti = self.evento.posti + 1
        with self.assertRaises(ValidationError):
            self.prenotazione.full_clean()


class AttesaEventoModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.luogo = create_luogo()
        self.evento = create_evento(posti=150, luogo=self.luogo)
        self.prenotazione = Prenotazione.objects.create(
            evento=self.evento,
            utente=self.user,
            posti=150
        )
        self.attesa = AttesaEvento.objects.create(evento=self.evento, utente=self.user)

    def test_attesa_creation(self):
        self.assertEqual(self.attesa.evento, self.evento)
        self.assertEqual(self.attesa.utente, self.user)

    def test_attesa_str(self):
        self.assertEqual(str(self.attesa), f'Attesa per {self.evento.titolo}')

    def test_attesa_unique_constraint(self):
        with self.assertRaises(Exception):
            AttesaEvento.objects.create(evento=self.evento, utente=self.user)

    def test_attesa_evento_required(self):
        with self.assertRaises(IntegrityError):
            AttesaEvento.objects.create(
                utente=self.user,
            )

    def test_attesa_utente_required(self):
        with self.assertRaises(IntegrityError):
            AttesaEvento.objects.create(
                evento=self.evento,
            )

    def test_attesa_evento_not_pieno(self):
        self.prenotazione.posti = 10
        self.prenotazione.save()
        with self.assertRaises(ValidationError):
            self.attesa.full_clean()


'''
 #TODO - FOLLOWING TESTS ARE TO BE REVIEWED YET
'''


class BaseViewsTests(TestCase):
    '''
    All these views do not require the user to be authenticated
    '''

    def setUp(self):
        self.client = Client()
        # Creazione di un utente per i test
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.luogo = create_luogo()
        self.evento_attivo = create_evento(
            titolo="Evento attivo",
            luogo=self.luogo
        )
        self.evento_passato = create_evento(
            titolo="Evento passato",
            descrizione="descrizione evento passato",
            data_ora=datetime.now() - timedelta(days=1),
            luogo=self.luogo
        )

    def test_lista_eventi_view(self):
        response = self.client.get(reverse('eventi:eventi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tutti gli eventi registrati")
        self.assertContains(response, "Evento attivo")
        self.assertNotContains(response, "Evento passato")

    def test_dettagli_evento_view(self):
        response = self.client.get(reverse('eventi:dettagli_evento', args=[self.evento_attivo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento attivo")

    def test_lista_luoghi_view(self):
        response = self.client.get(reverse('eventi:luoghi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luoghi")
        self.assertContains(response, "Luogo prova")

    def test_dettagli_luogo_view(self):
        response = self.client.get(reverse('eventi:dettagli_luogo', args=[self.luogo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luogo prova")
        self.assertContains(response, "Evento attivo")
        self.assertNotContains(response, "Evento passato")


class TestFunctionalViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        g = Group.objects.create(name="Visitatori")
        self.user.groups.add(g)
        self.client.login(username="testuser", password="password123")
        self.luogo = Luogo.objects.create(
            nome="Test Luogo",
            descrizione="Descrizione di test",
            indirizzo="Indirizzo test",
            sito_web="http://testsite.com"
        )
        self.evento = Evento.objects.create(
            titolo="Evento Attivo",
            descrizione="Descrizione evento attivo",
            posti=5,
            data_ora=datetime.now() + timedelta(days=1),
            luogo=self.luogo
        )

    def test_prenota_evento(self):
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), data={"posti": 2})
        self.assertEqual(response.status_code, 302)  # Redirect after booking
        self.assertTrue(Prenotazione.objects.filter(evento=self.evento, utente=self.user).exists())

    def test_prenota_evento_full(self):
        self.evento.posti = 0
        self.evento.save()
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]))
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        print(response)
        self.assertContains(response, "L'evento è esaurito!")

    def test_attesa_evento(self):
        self.evento.posti = 0
        self.evento.save()
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AttesaEvento.objects.filter(evento=self.evento, utente=self.user).exists())

    def test_interesse_evento(self):
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]))
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertTrue(self.evento.interessi.filter(id=self.user.id).exists())

        # Rimuovi interesse
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]))
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertFalse(self.evento.interessi.filter(id=self.user.id).exists())



    #     # Creazione di un utente
    #     g = Group.objects.create(name="Visitatori")
    #     self.user = User.objects.create_user(username='testuser', password='12345')
    #     self.user.groups.add(g)
    #     self.client.login(username='testuser', password='12345')
    #
    #
    # def test_prenota_evento_view(self):
    #     """Testa la prenotazione di un evento."""
    #     response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento1.pk]), {
    #         'posti': 1
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect dopo la prenotazione
    #     self.assertTrue(Prenotazione.objects.filter(evento=self.evento1, utente=self.user).exists())
    #
    # def test_attesa_evento_view(self):
    #     """Testa l'aggiunta di un utente alla lista d'attesa."""
    #     response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento1.pk]))
    #     self.assertEqual(response.status_code, 302)  # Redirect
    #     self.assertTrue(AttesaEvento.objects.filter(evento=self.evento1, utente=self.user).exists())
    #
    # def test_interesse_evento_view(self):
    #     """Testa l'aggiunta/rimozione dell'interesse per un evento."""
    #     response = self.client.post(reverse('eventi:interesse_evento', args=[self.evento1.pk]))
    #     self.assertEqual(response.status_code, 302)  # Redirect
    #     self.assertTrue(self.evento1.interessi.filter(id=self.user.id).exists())
    #
    #     # Testa la rimozione dell'interesse
    #     response = self.client.post(reverse('eventi:interesse_evento', args=[self.evento1.pk]))
    #     self.assertEqual(response.status_code, 302)  # Redirect
    #     self.assertFalse(self.evento1.interessi.filter(id=self.user.id).exists())
