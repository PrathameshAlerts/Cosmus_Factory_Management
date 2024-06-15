# Generated by Django 4.2.5 on 2024-06-15 07:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_alter_fabric_group_model_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawStockTransferMaster',
            fields=[
                ('voucher_no', models.AutoField(primary_key=True, serialize=False)),
                ('source_godown', models.CharField(max_length=200)),
                ('destination_godown', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RawStockTrasferRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name_transfer', models.CharField(max_length=200)),
                ('item_color_transfer', models.CharField(max_length=200)),
                ('item_shade_transfer', models.CharField(max_length=200)),
                ('item_quantity_transfer', models.CharField(max_length=200)),
                ('item_unit_transfer', models.CharField(max_length=200)),
                ('remarks', models.CharField(max_length=255)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('master_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.rawstocktransfermaster')),
            ],
        ),
        migrations.DeleteModel(
            name='RawStockTransfer',
        ),
    ]
