# Generated by Django 4.2.5 on 2024-03-14 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_id', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('return_reason', models.CharField(max_length=255)),
                ('batch_number', models.CharField(max_length=255)),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
        migrations.CreateModel(
            name='Return',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('notes', models.TextField()),
                ('return_status', models.CharField(choices=[('Pending', 'Pending'), ("'Received", "'Received"), ('Processed', 'Processed')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('return_date', models.DateTimeField()),
                ('return_reason', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('destination_location', models.CharField(max_length=255)),
                ('source_location', models.CharField(max_length=255)),
                ('return_reference', models.CharField(max_length=200)),
                ('logistics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logistics.logistic')),
                ('returnitems', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='returns.returnitems')),
            ],
        ),
    ]
