# Generated by Django 4.2.15 on 2024-11-27 10:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventi', '0003_evento_categoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prenotazione',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posti', models.IntegerField()),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prenotazioni', to='eventi.evento')),
                ('utente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prenotazioni', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Prenotazioni',
            },
        ),
    ]
