# Generated by Django 4.2.5 on 2024-03-27 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_remove_purchase_voucher_items_serial_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_purchase_voucher_master',
            name='ledger_type',
            field=models.CharField(default='purchase', max_length=20),
        ),
    ]
