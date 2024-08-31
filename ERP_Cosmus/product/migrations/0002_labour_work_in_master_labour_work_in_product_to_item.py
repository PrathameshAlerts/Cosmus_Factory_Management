# Generated by Django 4.2.5 on 2024-08-31 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='labour_work_in_master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_number', models.IntegerField(unique=True)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=100)),
                ('total_pcs', models.IntegerField()),
                ('total_pending_pcs', models.IntegerField()),
                ('total_return_pcs', models.IntegerField()),
                ('labour_charges', models.DecimalField(decimal_places=2, max_digits=10)),
                ('other_charges', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('modified_date', models.DateTimeField(auto_now_add=True)),
                ('labour_name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.ledger')),
                ('labour_voucher_number', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.labour_workout_childs')),
            ],
        ),
        migrations.CreateModel(
            name='labour_work_in_product_to_item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_sku', models.CharField(max_length=100)),
                ('product_color', models.CharField(max_length=100)),
                ('L_work_out_pcs', models.IntegerField()),
                ('return_pcs', models.IntegerField()),
                ('pending_to_return_pcs', models.IntegerField()),
                ('labour_workin_instance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='l_w_in_products', to='product.labour_work_in_master')),
            ],
        ),
    ]
