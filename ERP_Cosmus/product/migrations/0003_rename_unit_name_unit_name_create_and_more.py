# Generated by Django 4.2.5 on 2024-02-01 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_unit_name_alter_item_creation_fabric_group_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Unit_Name',
            new_name='Unit_Name_Create',
        ),
        migrations.RenameField(
            model_name='item_creation',
            old_name='Unit_Name',
            new_name='unit_name',
        ),
    ]
