# Generated by Django 4.2.5 on 2024-05-21 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_alter_product_2_item_through_table_common_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='set_prod_item_part_name',
            name='part_type',
        ),
        migrations.AddField(
            model_name='product_2_item_through_table',
            name='part_type',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
