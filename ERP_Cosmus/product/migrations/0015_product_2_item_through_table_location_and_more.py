# Generated by Django 4.2.5 on 2024-05-18 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_product_number_of_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_2_item_through_table',
            name='location',
            field=models.CharField(default=1, max_length=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='set_prod_item_part_name',
            name='part_pieces',
            field=models.IntegerField(default=0),
        ),
    ]
