# Generated by Django 4.2.15 on 2024-12-08 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventi', '0015_evento_image_luogo_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luogo',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='thumbnails/luoghi/'),
        ),
    ]
