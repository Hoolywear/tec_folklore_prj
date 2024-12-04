# Generated by Django 4.2.15 on 2024-12-03 10:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventi', '0009_alter_evento_thumbnail_alter_luogo_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='interessi',
            field=models.ManyToManyField(blank=True, related_name='interessi', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='evento',
            name='luogo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventi', to='eventi.luogo'),
        ),
    ]