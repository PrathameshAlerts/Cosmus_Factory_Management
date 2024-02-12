# Generated by Django 4.2.5 on 2024-02-12 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Product_Barcode', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CurrentStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('last_updated', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='InventoryLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_name', models.CharField(max_length=255)),
                ('location_type', models.CharField(max_length=255)),
                ('Store_type', models.CharField(choices=[('COCO', 'Compay Owned Company Operated'), ('FOCO', 'Company Owned Franchisee Operated'), ('COFO', 'Franchisee Owned Company Operated'), ('FOFO', 'Franchisee Owned Franchisee Operated')], max_length=255)),
                ('property_type', models.CharField(choices=[('Rented', 'Rented'), ('Shop in Shop', 'Shop in Shop')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='StockAdjustments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjusted_quantity', models.IntegerField()),
                ('reason', models.CharField(choices=[('Damaged Goods', 'Damaged Goods'), ('Inventory Reconciliation', 'Inventory Reconciliation'), ('Product Return', 'Product Return')], max_length=255)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('destination_location', models.CharField(max_length=255)),
                ('movement_date', models.DateTimeField()),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_details', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('mobile_no', models.CharField(max_length=255)),
                ('GST', models.CharField(max_length=30)),
                ('Company_Name', models.CharField(max_length=255)),
                ('Service_Type', models.CharField(choices=[('Product', 'Product'), ('Printing', 'Printing'), ('Logistic', 'Logistic')], max_length=254)),
                ('Email_id', models.EmailField(max_length=254)),
                ('description', models.TextField()),
            ],
        ),
    ]
