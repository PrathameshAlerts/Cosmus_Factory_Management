# Generated by Django 4.2.5 on 2024-02-19 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_alter_product_product_gst'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Product_GST',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.PROTECT, to='product.gst'),
        ),
    ]
