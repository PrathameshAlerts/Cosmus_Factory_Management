# Generated by Django 4.2.5 on 2024-07-26 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_alter_purchase_voucher_items_item_purchase_master_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='item_godown_inward_outward_master',
        ),
    ]
