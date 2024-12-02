# Generated by Django 4.2.15 on 2024-12-02 16:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('promozioni', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='promozione',
            old_name='utente',
            new_name='promotore',
        ),
        migrations.AlterField(
            model_name='promotore',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='promotore', to=settings.AUTH_USER_MODEL),
        ),
    ]