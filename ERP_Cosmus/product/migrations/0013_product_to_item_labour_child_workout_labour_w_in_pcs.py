# Generated by Django 4.2.5 on 2024-09-06 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_labour_work_in_product_to_item_pending_to_return_pcs'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_to_item_labour_child_workout',
            name='labour_w_in_pcs',
            field=models.IntegerField(default=56),
            preserve_default=False,
        ),
    ]
