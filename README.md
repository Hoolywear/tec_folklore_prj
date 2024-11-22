# HUB FOLKLORE 3.0

## Progetto di esame del corso di Tecnologie Web

Il progetto, ispirato dal contesto cittadino in cui vivo, consiste nello sviluppare una piattaforma web per la promozione di laboratori, corsi ed eventi (concerti, conferenze, eccetera) legati ai temi del folklore nella città di Gorizia e nel suo circondario.

## Operazioni necessarie all'installazione, librerie, eccetera

Richiede installati python 3.x, pip e pipenv

### Dipendenze pipenv

```shell
> pipenv graph

crispy-bootstrap5==2024.2
├── Django 
│   ├── asgiref 
│   │   └── typing_extensions 
│   └── sqlparse 
└── django-crispy-forms 
    └── Django 
        ├── asgiref 
        │   └── typing_extensions 
        └── sqlparse 
django-taggit==6.0.0
└── Django 
    ├── asgiref 
    │   └── typing_extensions 
    └── sqlparse 
pillow==10.4.0

> pipenv requirements

-i https://pypi.org/simple
asgiref==3.8.1; python_version >= '3.8'
crispy-bootstrap5==2024.2; python_version >= '3.8'
django==4.2.15; python_version >= '3.8'
django-crispy-forms==2.3; python_version >= '3.8'
django-taggit==6.0.0; python_version >= '3.8'
pillow==10.4.0; python_version >= '3.8'
sqlparse==0.5.1; python_version >= '3.8'
typing-extensions==4.12.2; python_version >= '3.8'
```
