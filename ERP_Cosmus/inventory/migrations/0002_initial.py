# Generated by Django 4.2.5 on 2024-03-12 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discount', '0001_initial'),
        ('logistics', '0001_initial'),
        ('product', '0001_initial'),
        ('inventory', '0001_initial'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovement',
            name='logistic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logistics.logistic'),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='source_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventorylocation'),
        ),
        migrations.AddField(
            model_name='stockadjustments',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventorylocation'),
        ),
        migrations.AddField(
            model_name='stockadjustments',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orders'),
        ),
        migrations.AddField(
            model_name='stockadjustments',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='stockadjustments',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.storemanager'),
        ),
        migrations.AddField(
            model_name='inventorylocation',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discount.discounts'),
        ),
        migrations.AddField(
            model_name='currentstock',
            name='Product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='currentstock',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventorylocation'),
        ),
        migrations.AddField(
            model_name='barcode',
            name='Product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]
