# Generated by Django 4.2.5 on 2024-09-03 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_ledgertypes_type_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='labour_charges',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ledger',
            name='vendor_code',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
