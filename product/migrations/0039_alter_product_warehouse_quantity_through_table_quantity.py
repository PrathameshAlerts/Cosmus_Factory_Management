# Generated by Django 4.2.5 on 2024-12-06 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0038_alter_finished_product_warehouse_bin_sub_catergory_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_warehouse_quantity_through_table',
            name='quantity',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]