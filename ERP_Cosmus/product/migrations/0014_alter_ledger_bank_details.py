# Generated by Django 4.2.5 on 2024-02-21 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_alter_ledger_maintain_billwise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='bank_details',
            field=models.TextField(blank=True),
        ),
    ]
