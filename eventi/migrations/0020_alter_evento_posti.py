# Generated by Django 4.2.15 on 2024-12-10 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventi', '0019_alter_evento_image_alter_luogo_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='posti',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
