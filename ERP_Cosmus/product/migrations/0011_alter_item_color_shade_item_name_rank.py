# Generated by Django 4.2.5 on 2024-02-24 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_alter_product_product_bulkprice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_color_shade',
            name='item_name_rank',
            field=models.PositiveIntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
