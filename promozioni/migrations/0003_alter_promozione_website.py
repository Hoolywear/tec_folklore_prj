# Generated by Django 4.2.15 on 2024-12-02 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promozioni', '0002_rename_utente_promozione_promotore_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promozione',
            name='website',
            field=models.URLField(unique=True),
        ),
    ]
