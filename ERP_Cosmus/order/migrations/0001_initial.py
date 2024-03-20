# Generated by Django 4.2.5 on 2024-03-20 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
        ('discount', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Product_Discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discount.discounts')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Net 30', 'Net 30'), ('50 upfront', '50 upfront'), ('COD', 'Cash on Delivery')], max_length=255)),
                ('description', models.TextField()),
                ('days_to_payment', models.DateField()),
                ('percentage_due', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_active', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StoreManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('StoreManager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Partially Paid', 'Partially Paid'), ('Paid', 'Paid'), ('Overdue', 'Overdue')], max_length=50)),
                ('percentage_of_total', models.DecimalField(decimal_places=2, max_digits=5)),
                ('days_from_order', models.DateField()),
                ('payment_due_date', models.DateField()),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=5)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=5)),
                ('payment_method', models.CharField(choices=[('Credit Card', 'Credit Card'), ('Bank Transfer', 'Bank Transfer'), ('Cash', 'Cash')], max_length=50)),
                ('payment_reference', models.CharField(max_length=255)),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('payment_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.paymentterm')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Under_Production', 'Under_Production'), ('Quality Check', 'Quality Check'), ('Ready to Ship', 'Ready to Ship'), ('In Transit', 'InTransit'), ('Delivered', 'Delivered')], max_length=50)),
                ('total_amount', models.DecimalField(decimal_places=3, max_digits=9)),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('total_due', models.DecimalField(decimal_places=2, max_digits=5)),
                ('total_paid', models.DecimalField(decimal_places=2, max_digits=5)),
                ('balance_due', models.DecimalField(decimal_places=2, max_digits=5)),
                ('Customer_Name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.customer')),
                ('Items', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orderitem')),
                ('Stock_Movement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.stockmovement')),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discount.discounts')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=5)),
                ('payment_date', models.DateField(auto_now=True)),
                ('payment_method', models.CharField(choices=[('Credit Card', 'Credit Card'), ('Bank Transfer', 'Bank Transfer'), ('Cash', 'Cash'), ('Cheque', 'Cheque')], max_length=50)),
                ('payment_reference', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('Completed', 'Completed'), ('Pending', 'Pending'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], max_length=255)),
                ('currency', models.CharField(choices=[('USD', 'USD'), ('INR', 'INR'), ('EUR', 'EUR')], max_length=255)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.storemanager')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orders')),
                ('payment_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.paymentschedule')),
            ],
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orders'),
        ),
    ]
