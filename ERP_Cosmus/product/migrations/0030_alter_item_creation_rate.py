# Generated by Django 4.2.5 on 2024-06-26 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_rename_total_comsuption_purchase_order_for_raw_material_total_comsumption_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_creation',
            name='rate',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10),
        ),
    ]
