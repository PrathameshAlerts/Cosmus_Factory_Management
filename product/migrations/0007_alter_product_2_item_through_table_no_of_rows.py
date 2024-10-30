# Generated by Django 4.2.5 on 2024-10-18 12:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_purchase_order_to_product_product_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_2_item_through_table',
            name='no_of_rows',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]