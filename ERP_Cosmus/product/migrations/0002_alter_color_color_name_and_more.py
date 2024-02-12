# Generated by Django 4.2.5 on 2024-02-12 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='color_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='fabric_group_model',
            name='fab_grp_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='unit_name_create',
            name='unit_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
