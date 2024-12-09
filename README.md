# HUB FOLKLORE 3.0

## Progetto di esame del corso di Tecnologie Web

Il progetto, ispirato dal contesto cittadino in cui vivo, consiste nello sviluppare una piattaforma web per la promozione di laboratori, corsi ed eventi (concerti, conferenze, eccetera) legati ai temi del folklore nella città di Gorizia e nel suo circondario.

---
***AVVISO: Le bozze del testo nella pagina About e delle descrizioni di eventi e luoghi sono stati generati da ChatGPT a partire dalla mia descrizione del progetto, e successivamente corretti e rivisti a mano.***

---

## Operazioni necessarie all'installazione, librerie, eccetera

Richiede installati python 3.10.16, pip 24.3.1 e pipenv 2024.4.0

```shell

```

### Dipendenze pipenv
Le dipendenze sono riportate qui di seguito come informazione aggiuntiva.
Il file in cui si trovano i requisiti più *up to date* è `requirements.txt` (si tenga conto di quello per 
l'installazione dei pacchetti)

```shell

> pipenv requirements

-i https://pypi.org/simple
asgiref==3.8.1; python_version >= '3.8'
crispy-bootstrap5==2024.2; python_version >= '3.8'
da-vinci==0.4.0
django==4.2.15; python_version >= '3.8'
django-braces==1.16.0
django-crispy-forms==2.3; python_version >= '3.8'
django-extensions==3.2.3; python_version >= '3.6'
django-taggit==6.0.0; python_version >= '3.8'
django-thumbnails==0.8.0
pillow==10.4.0; python_version >= '3.8'
shortuuid==1.0.13; python_version >= '3.6'
sqlparse==0.5.1; python_version >= '3.8'
typing-extensions==4.12.2; python_version >= '3.8'
```

### Installazione dei pacchetti

```shell
pipenv install -r requirements.txt
```

### Importazione dati di prova

Il primo popolamento avviene mediante funzioni definite in `initcmds.py`, 
le quali sono eseguite ad ogni restart del server (le troviamo in `hub_folklore/urls.py`)
e caricano luoghi ed eventi da appositi file JSON (simili alle fixtures, ma con alcuni workaround ad es. per il
caricamento di immagini).