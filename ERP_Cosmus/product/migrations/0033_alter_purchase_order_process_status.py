# Generated by Django 4.2.5 on 2024-06-28 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0032_purchase_order_process_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase_order',
            name='process_status',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
