# Generated by Django 4.2.5 on 2024-02-26 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_alter_godown_godown_material_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='godown',
            name='godown_material_name',
        ),
    ]
