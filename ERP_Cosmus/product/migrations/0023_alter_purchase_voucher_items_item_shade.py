# Generated by Django 4.2.5 on 2024-06-21 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_alter_rawstocktransfermaster_destination_godown_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase_voucher_items',
            name='item_shade',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.item_color_shade'),
        ),
    ]
