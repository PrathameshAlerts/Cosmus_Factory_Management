# Generated by Django 4.2.5 on 2024-11-22 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0028_finished_goods_stock_transfermaster_transnfer_cancelled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labour_work_in_product_to_item',
            name='product_sku',
            field=models.PositiveBigIntegerField(),
        ),
    ]
