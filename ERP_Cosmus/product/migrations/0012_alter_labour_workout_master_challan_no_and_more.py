# Generated by Django 4.2.5 on 2024-07-31 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_labour_workout_master_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labour_workout_master',
            name='challan_no',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='labour_workout_master',
            name='total_approved_pcs',
            field=models.IntegerField(),
        ),
    ]
