# Generated by Django 4.2.5 on 2024-10-15 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0038_purchase_order_for_raw_material_pcs'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
