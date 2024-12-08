# Generated by Django 4.2.15 on 2024-12-08 07:16

from django.conf import settings
from django.db import migrations, models
import eventi.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventi', '0012_alter_evento_luogo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prenotazione',
            name='utente',
            field=models.ForeignKey(on_delete=models.SET(eventi.models.get_sentinel_user), related_name='prenotazioni', to=settings.AUTH_USER_MODEL),
        ),
    ]