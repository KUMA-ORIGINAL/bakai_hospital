# Generated by Django 5.1 on 2025-03-12 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_remove_user_services'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('accountant', 'Бухгалтер'), ('doctor', 'Врач'), ('admin', 'Админ')], max_length=20, verbose_name='Роль'),
        ),
    ]
