# Generated by Django 4.2.5 on 2024-05-22 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_alter_product_2_item_through_table_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_2_item_through_table',
            name='no_of_rows',
            field=models.IntegerField(default=0),
        ),
    ]
