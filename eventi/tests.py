from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User, Group

from hub_folklore import settings
from .models import Luogo, Evento, Prenotazione, AttesaEvento
from datetime import datetime, timedelta


class LuogoModelTest(TestCase):

    def setUp(self):
        self.luogo = Luogo.objects.create(
            nome="Luogo prova",
            descrizione="descrizione prova",
            indirizzo="indirizzo prova",
            sito_web="https://www.prova.it"
        )

    def test_luogo_creation(self):
        self.assertEqual(self.luogo.nome, "Luogo prova")
        self.assertEqual(self.luogo.descrizione, "descrizione prova")
        self.assertEqual(self.luogo.indirizzo, "indirizzo prova")
        self.assertEqual(self.luogo.sito_web, "https://www.prova.it")

    def test_luogo_str(self):
        self.assertEqual(str(self.luogo), "Luogo prova")

    def test_luogo_default_image(self):
        self.assertEqual(self.luogo.image.path, settings.MEDIA_ROOT+'/imgs/def_imgs/thumb_1.jpg')

    def test_luogo_nome_required(self):
        self.assertRaises(ValueError, Luogo.objects.create())

class EventoModelTest(TestCase):

    def setUp(self):
        self.luogo = Luogo.objects.create(
            nome="Castello di Gorizia",
            descrizione="Antica fortezza medievale con vista mozzafiato.",
            indirizzo="Via del Castello, 36, Gorizia",
            sito_web="https://www.castellodigorizia.it"
        )
        self.evento = Evento.objects.create(
            titolo="Concerto al Castello",
            descrizione="Un emozionante concerto di musica classica.",
            posti=100,
            data_ora=datetime.now() + timedelta(days=1),
            categoria="concerto",
            luogo=self.luogo
        )

    def test_evento_creation(self):
        self.assertEqual(self.evento.titolo, "Concerto al Castello")
        self.assertEqual(self.evento.categoria, "concerto")
        self.assertEqual(str(self.evento), "Concerto al Castello")
        self.assertTrue(self.evento.evento_attivo())

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


class PrenotazioneModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.luogo = Luogo.objects.create(
            nome="Museo della Grande Guerra",
            descrizione="Museo dedicato alla Prima Guerra Mondiale.",
            indirizzo="Borgo Castello, 13, Gorizia",
            sito_web="https://www.museograndeguerra.it"
        )
        self.evento = Evento.objects.create(
            titolo="Visita guidata",
            descrizione="Visita guidata alle esposizioni del museo.",
            posti=50,
            data_ora=datetime.now() + timedelta(days=3),
            categoria="mostra",
            luogo=self.luogo
        )
        self.prenotazione = Prenotazione.objects.create(
            evento=self.evento,
            utente=self.user,
            posti=5
        )

    def test_prenotazione_creation(self):
        self.assertEqual(self.prenotazione.evento, self.evento)
        self.assertEqual(self.prenotazione.utente, self.user)
        self.assertEqual(self.prenotazione.posti, 5)
        self.assertEqual(str(self.prenotazione), f'Prenotazione per {self.evento.titolo} (posti: 5)')

    def test_prenotazione_unique_constraint(self):
        with self.assertRaises(Exception):
            Prenotazione.objects.create(evento=self.evento, utente=self.user, posti=5)


class AttesaEventoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser2")
        self.luogo = Luogo.objects.create(
            nome="Auditorium di Gorizia",
            descrizione="Sala concerti moderna con acustica eccellente.",
            indirizzo="Via Roma, 6, Gorizia",
            sito_web="https://www.auditoriumgorizia.it"
        )
        self.evento = Evento.objects.create(
            titolo="Concerto Jazz",
            descrizione="Un viaggio nella musica jazz con artisti internazionali.",
            posti=150,
            data_ora=datetime.now() + timedelta(days=5),
            categoria="concerto",
            luogo=self.luogo
        )
        self.attesa = AttesaEvento.objects.create(evento=self.evento, utente=self.user)

    def test_attesa_creation(self):
        self.assertEqual(self.attesa.evento, self.evento)
        self.assertEqual(self.attesa.utente, self.user)
        self.assertEqual(str(self.attesa), f'Attesa per {self.evento.titolo}')

    def test_attesa_unique_constraint(self):
        with self.assertRaises(Exception):
            AttesaEvento.objects.create(evento=self.evento, utente=self.user)


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from eventi.models import Luogo, Evento, Prenotazione, AttesaEvento
from datetime import datetime, timedelta


class TestClassBasedViews(TestCase):

    def setUp(self):
        # Creazione di un utente per i test
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.luogo = Luogo.objects.create(
            nome="Test Luogo",
            descrizione="Descrizione di test",
            indirizzo="Indirizzo test",
            sito_web="http://testsite.com"
        )
        self.evento_attivo = Evento.objects.create(
            titolo="Evento Attivo",
            descrizione="Descrizione evento attivo",
            posti=10,
            data_ora=datetime.now() + timedelta(days=1),
            luogo=self.luogo
        )
        self.evento_passato = Evento.objects.create(
            titolo="Evento Passato",
            descrizione="Descrizione evento passato",
            posti=10,
            data_ora=datetime.now() - timedelta(days=1),
            luogo=self.luogo
        )

    def test_lista_eventi_view(self):
        response = self.client.get(reverse('eventi:eventi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento Attivo")
        self.assertNotContains(response, "Evento Passato")

    def test_dettagli_evento_view(self):
        response = self.client.get(reverse('eventi:dettagli_evento', args=[self.evento_attivo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento Attivo")

    def test_lista_luoghi_view(self):
        response = self.client.get(reverse('eventi:luoghi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Luogo")

    def test_dettagli_luogo_view(self):
        response = self.client.get(reverse('eventi:dettagli_luogo', args=[self.luogo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Luogo")
        self.assertContains(response, "Evento Attivo")
        self.assertNotContains(response, "Evento Passato")


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


class TestFilteredViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.luogo = Luogo.objects.create(
            nome="Test Luogo",
            descrizione="Descrizione di test",
            indirizzo="Indirizzo test",
            sito_web="http://testsite.com"
        )
        self.evento = Evento.objects.create(
            titolo="Evento con Tag",
            descrizione="Descrizione evento con tag",
            posti=10,
            data_ora=datetime.now() + timedelta(days=1),
            luogo=self.luogo
        )
        self.evento.tags.add("Concerto")

    def test_lista_eventi_tag_view(self):
        response = self.client.get(reverse('eventi:eventi_tag', args=["Concerto"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento con Tag")

    def test_lista_eventi_ricerca_view(self):
        pass


from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from eventi.models import Luogo, Evento, Prenotazione, AttesaEvento
from datetime import datetime, timedelta


class EventiViewsTest(TestCase):

    def setUp(self):
        # Creazione del client
        self.client = Client()

        # Creazione di un utente
        g = Group.objects.create(name="Visitatori")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.groups.add(g)
        self.client.login(username='testuser', password='12345')

        # Creazione di un luogo
        self.luogo = Luogo.objects.create(
            nome="Teatro Verdi",
            descrizione="Storico teatro.",
            indirizzo="Piazza Vittoria, 1",
            sito_web="https://www.teatroverdi.it"
        )

        # Creazione di eventi
        self.evento1 = Evento.objects.create(
            titolo="Concerto Jazz",
            descrizione="Un concerto di musica jazz.",
            posti=50,
            data_ora=datetime.now() + timedelta(days=10),
            categoria='concerto',
            luogo=self.luogo
        )
        self.evento2 = Evento.objects.create(
            titolo="Mostra di Arte Moderna",
            descrizione="Esposizione di opere d'arte moderna.",
            posti=20,
            data_ora=datetime.now() - timedelta(days=5),
            categoria='mostra',
            luogo=self.luogo
        )

    def test_lista_eventi_view(self):
        """Testa la visualizzazione della lista degli eventi."""
        response = self.client.get(reverse('eventi:eventi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento1.titolo)
        self.assertNotContains(response, self.evento2.titolo)  # Non deve mostrare eventi passati

    def test_dettagli_evento_view(self):
        """Testa la visualizzazione dei dettagli di un evento."""
        response = self.client.get(reverse('eventi:dettagli_evento', args=[self.evento1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.evento1.titolo)
        self.assertContains(response, self.evento1.descrizione)

    def test_lista_luoghi_view(self):
        """Testa la visualizzazione della lista dei luoghi."""
        response = self.client.get(reverse('eventi:luoghi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.luogo.nome)

    def test_dettagli_luogo_view(self):
        """Testa la visualizzazione dei dettagli di un luogo."""
        response = self.client.get(reverse('eventi:dettagli_luogo', args=[self.luogo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.luogo.nome)
        self.assertContains(response, self.luogo.descrizione)

    def test_prenota_evento_view(self):
        """Testa la prenotazione di un evento."""
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento1.pk]), {
            'posti': 1
        })
        self.assertEqual(response.status_code, 302)  # Redirect dopo la prenotazione
        self.assertTrue(Prenotazione.objects.filter(evento=self.evento1, utente=self.user).exists())

    def test_attesa_evento_view(self):
        """Testa l'aggiunta di un utente alla lista d'attesa."""
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento1.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(AttesaEvento.objects.filter(evento=self.evento1, utente=self.user).exists())

    def test_interesse_evento_view(self):
        """Testa l'aggiunta/rimozione dell'interesse per un evento."""
        response = self.client.post(reverse('eventi:interesse_evento', args=[self.evento1.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(self.evento1.interessi.filter(id=self.user.id).exists())

        # Testa la rimozione dell'interesse
        response = self.client.post(reverse('eventi:interesse_evento', args=[self.evento1.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(self.evento1.interessi.filter(id=self.user.id).exists())
