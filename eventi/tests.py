from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.template.defaultfilters import date as filter_date

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
    if posti is not None:
        evento.posti = posti
    if categoria is not None:
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


class SearchViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.luogo = create_luogo()
        self.evento = create_evento(titolo="Evento con Tag", luogo=self.luogo)
        self.evento.tags.add("tag1")
        self.evento2 = create_evento(titolo="Evento con un altro tag", luogo=self.luogo)
        self.evento2.tags.add("tag2")
        self.evento_lab = create_evento(
            titolo="Evento laboratorio",
            luogo=self.luogo,
            categoria='laboratorio'
        )
        self.evento_futuro = create_evento(
            titolo="Evento futuro",
            luogo=self.luogo,
            data_ora=day_start(datetime.now() + timedelta(days=2)),
        )
        self.evento_passato = create_evento(
            titolo="Evento passato",
            luogo=self.luogo,
            data_ora=day_start(datetime.now() - timedelta(days=1)),
        )

    def test_lista_eventi_tag_view(self):
        response = self.client.get(reverse('eventi:eventi_tag', args=["tag1"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['titolo'], "Eventi con tag 'tag1'")
        self.assertEqual(response.context['tag'], "tag1")
        self.assertContains(response, "Evento con Tag")
        self.assertNotContains(response, "Evento con un altro tag")
        self.assertQuerysetEqual(response.context['object_list'].all(), [self.evento])

    def test_lista_eventi_tag_view_empty(self):
        response = self.client.get(reverse('eventi:eventi_tag', args=["tag"]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'].all(), [])
        self.assertContains(response, "Nessun evento trovato.")

    def test_lista_eventi_risultati_view_all(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': 'all',
            'from_d': date.today().strftime('%Y-%m-%d')}))
        self.assertQuerysetEqual(response.context['object_list'].all(),
                                 Evento.active_objects.all())
        self.assertContains(response, "Evento con Tag")
        self.assertContains(response, "Evento con un altro tag")
        self.assertContains(response, "Tutti gli eventi")

    def test_lista_eventi_risultati_view_correct_categoria(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': self.evento_lab.categoria,
            'from_d': date.today().strftime('%Y-%m-%d')}))
        self.assertQuerysetEqual(response.context['object_list'].all(), [self.evento_lab])
        self.assertContains(response, "Evento laboratorio")
        self.assertNotContains(response, "Evento con tag")
        self.assertContains(response, dict(Evento.CATEGORY_CHOICES)[self.evento_lab.categoria])

    def test_lista_eventi_risultati_view_wrong_categoria(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': 'categoria inesistente',
            'from_d': date.today().strftime('%Y-%m-%d')}), follow=True)
        self.assertRedirects(response, reverse('search'))
        self.assertRaisesMessage(Exception, "Categoria non valida")

    def test_lista_eventi_risultati_view_correct_data(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': 'all',
            'from_d': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')}))
        self.assertQuerysetEqual(response.context['object_list'], [self.evento_futuro])
        self.assertContains(response, "Evento futuro")
        self.assertContains(response, f"Tutti gli eventi")
        self.assertContains(response, f" dal {filter_date(response.context['from_d'])}")

    def test_lista_eventi_risultati_view_wrong_data(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': 'categoria inesistente',
            'from_d': 'whatever wrong formatted string'}), follow=True)
        self.assertRedirects(response, reverse('search'))
        self.assertRaisesMessage(Exception, "Data non valida")

    def test_lista_eventi_risultati_view_past_data(self):
        response = self.client.get(reverse('eventi:risultati_ricerca', kwargs={
            'categoria': 'categoria inesistente',
            'from_d': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')}), follow=True)
        self.assertRedirects(response, reverse('search'))
        self.assertRaisesMessage(Exception, "Data non valida")

    def test_lista_eventi_risultati_q_view_all(self):
        response = self.client.get(reverse('eventi:risultati_ricerca_q', kwargs={
            'categoria': 'all',
            'from_d': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'q': 'lab'
        }))
        self.assertQuerysetEqual(response.context['object_list'].all(), [self.evento_lab])
        self.assertContains(response, f"Tutti gli eventi")
        self.assertContains(response, f" dal {filter_date(response.context['from_d'])}")
        self.assertContains(response, f" che corrispondono a '{response.context['q']}'")


class PrenotazioneViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_visitatore = User.objects.create_user(username="visitatore", password="password123")
        visitatori = Group.objects.create(name='Visitatori')
        self.user_visitatore.groups.add(visitatori)

        self.user_not_visitatore = User.objects.create_user(username="testuser", password="password123")

        self.luogo = create_luogo()
        self.evento = create_evento(
            luogo=self.luogo
        )

    def test_prenota_evento_login(self):
        response = self.client.get(reverse('eventi:prenota_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response,
                             reverse('users:login')+'?auth=notok&next='+reverse('eventi:prenota_evento', args=[self.evento.pk]))

    def test_prenota_evento_404(self):
        self.client.login(username="visitatore", password="password123")
        old_pk = self.evento.pk
        self.evento.delete()
        response = self.client.get(reverse('eventi:prenota_evento', args=[old_pk]))
        self.assertEqual(response.status_code, 404)

    def test_prenota_evento_403(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse('eventi:prenota_evento', args=[self.evento.pk]))
        self.assertEqual(response.status_code, 403)

    def test_prenota_evento_evento_passato(self):
        self.evento.data_ora = day_start(datetime.today() - timedelta(days=1))
        self.evento.save()
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:prenota_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:eventi'))
        self.assertRaisesMessage(Exception, "L'evento è passato!")

    def test_prenota_evento_evento_esaurito(self):
        self.evento.posti = 0
        self.evento.save()
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:prenota_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertRaisesMessage(Exception, "L'evento è esaurito!")

    def test_prenota_evento_gia_prenotato(self):
        Prenotazione.objects.create(utente=self.user_visitatore, evento=self.evento, posti=5)
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:prenota_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertRaisesMessage(Exception, "Hai già una prenotazione per questo evento!")

    def test_prenota_evento_dati_corretti(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), {'posti': 1}, follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertContains(response, "Evento prenotato!")
        self.assertEqual(Prenotazione.objects.filter(evento=self.evento, utente=self.user_visitatore).count(), 1)

    def test_prenota_evento_esiste_attesa(self):
        AttesaEvento.objects.create(evento=self.evento, utente=self.user_visitatore)
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), {'posti': 1}, follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertContains(response, "Evento prenotato!")
        self.assertQuerysetEqual(AttesaEvento.objects.filter(evento=self.evento, utente=self.user_visitatore), [])
        self.assertEqual(Prenotazione.objects.filter(evento=self.evento, utente=self.user_visitatore).count(), 1)

    def test_prenota_evento_dati_scorretti_posti_negativi(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), {'posti': -1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(Prenotazione.objects.filter(evento=self.evento, utente=self.user_visitatore), [])


    def test_prenota_evento_dati_scorretti_posti_zero(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), {'posti': 0}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(Prenotazione.objects.filter(evento=self.evento, utente=self.user_visitatore), [])

    def test_prenota_evento_posti_eccedono_disponibili(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:prenota_evento', args=[self.evento.pk]), {'posti': 11}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRaisesMessage(Exception, f"I posti disponibili non sono sufficienti (rimangono {self.evento.posti_disponibili()} posti)")
        self.assertQuerysetEqual(Prenotazione.objects.filter(evento=self.evento, utente=self.user_visitatore), [])


class AttesaViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_visitatore = User.objects.create_user(username="visitatore", password="password123")
        visitatori = Group.objects.create(name='Visitatori')
        self.user_visitatore.groups.add(visitatori)

        self.user_not_visitatore = User.objects.create_user(username="testuser", password="password123")

        self.luogo = create_luogo()
        self.evento = create_evento(
            luogo=self.luogo
        )
        self.evento_esaurito = create_evento(
            luogo=self.luogo,
            posti=0
        )

    def test_attesa_evento_login(self):
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response,
                             reverse('users:login')+'?auth=notok&next='+reverse('eventi:waitlist_evento', args=[self.evento.pk]))

    def test_attesa_evento_404(self):
        self.client.login(username="visitatore", password="password123")
        old_pk = self.evento.pk
        self.evento.delete()
        response = self.client.get(reverse('eventi:waitlist_evento', args=[old_pk]))
        self.assertEqual(response.status_code, 404)

    def test_attesa_evento_403(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]))
        self.assertEqual(response.status_code, 403)

    def test_attesa_evento_evento_passato(self):
        self.evento.data_ora = day_start(datetime.today() - timedelta(days=1))
        self.evento.save()
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:eventi'))
        self.assertRaisesMessage(Exception, "L'evento è passato!")

    def test_attesa_evento_evento_non_esaurito(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertRaisesMessage(Exception, "L'evento ha ancora posti disponibili")

    def test_attesa_evento_gia_prenotato(self):
        Prenotazione.objects.create(utente=self.user_visitatore, evento=self.evento, posti=5)
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:waitlist_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertRaisesMessage(Exception, "Hai già una prenotazione per l'evento!")

    def test_attesa_evento_dati_corretti(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:waitlist_evento', args=[self.evento_esaurito.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento_esaurito.pk]))
        self.assertEqual(AttesaEvento.objects.filter(evento=self.evento_esaurito, utente=self.user_visitatore).count(), 1)

    def test_attesa_evento_esiste_attesa(self):
        AttesaEvento.objects.create(evento=self.evento_esaurito, utente=self.user_visitatore)
        self.client.login(username="visitatore", password="password123")
        response = self.client.post(reverse('eventi:waitlist_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertRaisesMessage(Exception, "Sei già in lista di attesa!")
        self.assertEqual(AttesaEvento.objects.filter(evento=self.evento_esaurito, utente=self.user_visitatore).count(), 1)


class InteresseViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_visitatore = User.objects.create_user(username="visitatore", password="password123")
        visitatori = Group.objects.create(name='Visitatori')
        self.user_visitatore.groups.add(visitatori)

        self.user_not_visitatore = User.objects.create_user(username="testuser", password="password123")

        self.luogo = create_luogo()
        self.evento = create_evento(
            luogo=self.luogo
        )

    def test_interesse_evento_login(self):
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response,
                             reverse('users:login')
                             + '?auth=notok&next='
                             + reverse('eventi:interesse_evento', args=[self.evento.pk]))

    def test_interesse_evento_404(self):
        self.client.login(username="visitatore", password="password123")
        old_pk = self.evento.pk
        self.evento.delete()
        response = self.client.get(reverse('eventi:interesse_evento', args=[old_pk]))
        self.assertEqual(response.status_code, 404)

    def test_interesse_evento_403(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]))
        self.assertEqual(response.status_code, 403)

    def test_attesa_evento_evento_passato(self):
        self.evento.data_ora = day_start(datetime.today() - timedelta(days=1))
        self.evento.save()
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:eventi'))
        self.assertRaisesMessage(Exception, "Evento passato")
        self.assertQuerySetEqual(self.user_visitatore.interessi.all(), [])

    def test_attesa_evento_evento_passato_rimuovi_interesse(self):
        self.evento.data_ora = day_start(datetime.today() - timedelta(days=1))
        self.evento.save()
        self.evento.interessi.add(self.user_visitatore)
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertQuerySetEqual(self.user_visitatore.interessi.all(), [])

    def test_attesa_evento_aggiungi_interesse(self):
        self.client.login(username="visitatore", password="password123")
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]), follow=True)
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertQuerysetEqual(self.user_visitatore.interessi.all(), [self.evento])

    def test_attesa_evento_rimuovi_interesse(self):
        self.client.login(username="visitatore", password="password123")
        self.evento.interessi.add(self.user_visitatore)
        response = self.client.get(reverse('eventi:interesse_evento', args=[self.evento.pk]))
        self.assertRedirects(response, reverse('eventi:dettagli_evento', args=[self.evento.pk]))
        self.assertQuerysetEqual(self.user_visitatore.interessi.all(), [])
