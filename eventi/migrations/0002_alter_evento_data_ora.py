# Generated by Django 4.2.15 on 2024-11-25 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='data_ora',
            field=models.DateTimeField(),
        ),
    ]