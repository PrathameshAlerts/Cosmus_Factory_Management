# Generated by Django 4.2.10 on 2024-02-14 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipment_date', models.DateField(auto_now=True)),
                ('movement_type', models.CharField(choices=[('Inbound', 'Inbound'), ('Outbound', 'Outbound'), ('Stock Adjustment', 'Stock Adjustment'), ('Return', 'Return')], max_length=50)),
                ('expected_delivery_date', models.DateField()),
                ('actual_delivery_date', models.DateField()),
                ('tracking_number', models.IntegerField()),
                ('carrier', models.CharField(choices=[('UPS', 'UPS'), ('DTDC', 'DTDC'), ('Express Delivery', 'Express Delivery')], max_length=50)),
                ('status', models.CharField(choices=[('In Transit', 'In Transit'), ('Delivered', 'Delivered')], max_length=50)),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('Expected_Cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Actual_Cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orders')),
            ],
        ),
    ]
