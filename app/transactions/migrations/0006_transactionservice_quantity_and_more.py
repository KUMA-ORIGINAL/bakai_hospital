# Generated by Django 5.1 on 2025-03-29 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_alter_transactionservice_service_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionservice',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='historicaltransaction',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Общая сумма'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Общая сумма'),
        ),
    ]
