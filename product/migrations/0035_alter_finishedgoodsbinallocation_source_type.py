# Generated by Django 4.2.5 on 2024-11-30 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0034_finished_goods_warehouse_racks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finishedgoodsbinallocation',
            name='source_type',
            field=models.CharField(choices=[('purchase', 'purchase'), ('transfer', 'transfer')], max_length=20),
        ),
    ]
