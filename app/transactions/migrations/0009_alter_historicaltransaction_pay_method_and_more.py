# Generated by Django 5.1 on 2025-04-15 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0008_alter_historicaltransaction_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltransaction',
            name='pay_method',
            field=models.CharField(choices=[('bakai_bank', 'Bakai Bank')], default='bakai_bank', max_length=50, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='pay_method',
            field=models.CharField(choices=[('bakai_bank', 'Bakai Bank')], default='bakai_bank', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
