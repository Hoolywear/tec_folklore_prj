# Generated by Django 4.2.15 on 2024-12-08 14:01

from django.db import migrations
import thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('promozioni', '0006_promozione_visite_anonime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promozione',
            name='banner',
            field=thumbnails.fields.ImageField(upload_to='promozioni/banners/'),
        ),
    ]
