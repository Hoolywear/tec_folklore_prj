# Generated by Django 4.2.15 on 2024-12-08 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventi', '0011_alter_evento_thumbnail_alter_luogo_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='luogo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='eventi', to='eventi.luogo'),
        ),
    ]
