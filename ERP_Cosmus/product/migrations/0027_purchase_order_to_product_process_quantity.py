# Generated by Django 4.2.5 on 2024-06-25 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_rename_quantity_purchase_order_to_product_order_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order_to_product',
            name='process_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
