# Generated by Django 4.2.5 on 2024-08-01 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_labour_workout_master_challan_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order_to_product_cutting',
            name='balance_pcs',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='labour_workout_master',
            name='total_approved_pcs',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='labour_workout_master',
            name='total_pending_pcs',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
