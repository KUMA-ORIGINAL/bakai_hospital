# Generated by Django 5.1 on 2025-03-08 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_user_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='patronymic',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('accountant', 'Бухгалтер'), ('doctor', 'Врач'), ('admin', 'Админ')], default='doctor', max_length=20, verbose_name='Роль'),
        ),
    ]
