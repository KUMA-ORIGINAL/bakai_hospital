# Generated by Django 5.1 on 2025-04-19 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_rename_birthdate_patient_date_of_birth'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('-date_joined',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]
