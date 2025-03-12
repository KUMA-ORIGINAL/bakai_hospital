# Generated by Django 5.1 on 2025-03-10 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='pay_method',
            field=models.CharField(choices=[('cash', 'Наличные'), ('bakai_bank', 'Bakai Bank')], max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
