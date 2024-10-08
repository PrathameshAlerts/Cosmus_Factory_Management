# Generated by Django 4.2.5 on 2024-09-21 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_customuser_is_admin'),
        ('product', '0010_remove_stockitem_company_name_stockitem_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='stock_item_name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterUniqueTogether(
            name='stockitem',
            unique_together={('stock_item_name', 'company')},
        ),
    ]
