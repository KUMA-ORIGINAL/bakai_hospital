# Generated by Django 5.1 on 2025-04-15 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_alter_payoutaccount_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payoutaccount',
            name='payout_token',
            field=models.TextField(verbose_name='Токен для выплат'),
        ),
    ]
