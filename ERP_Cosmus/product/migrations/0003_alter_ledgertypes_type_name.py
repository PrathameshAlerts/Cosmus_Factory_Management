# Generated by Django 4.2.5 on 2024-09-02 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_labour_work_in_master_labour_work_in_product_to_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledgertypes',
            name='type_name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
