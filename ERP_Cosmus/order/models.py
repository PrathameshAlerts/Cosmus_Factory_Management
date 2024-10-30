from django.db import models
from discount.models import Discounts
from product.models import Product
from django.conf import settings
from product.models import Customer


class StoreManager(models.Model):
    StoreManager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Orders(models.Model):
    STATUS = [
        ("Pending","Pending"),
        ("Under_Production","Under_Production"),
        ("Quality Check","Quality Check"),
        ("Ready to Ship","Ready to Ship"),
        ("In Transit","InTransit"),
        ("Delivered","Delivered"),

    ]
    Customer_Name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now=True)
    Items = models.ForeignKey('OrderItem' , on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS)
    total_amount = models.DecimalField(max_digits=9, decimal_places=3)
    discount =  models.ForeignKey(Discounts , on_delete=models.CASCADE)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    Stock_Movement = models.ForeignKey("inventory.StockMovement", on_delete=models.CASCADE)
    total_due = models.CharField(max_length=255)
    total_paid = models.CharField(max_length=255)
    balance_due = models.CharField(max_length=255)
    total_due = models.DecimalField(max_digits=5, decimal_places=2)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2)
    balance_due = models.DecimalField(max_digits=5, decimal_places=2)



class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product: models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity: models.IntegerField()
    unit_price: models.DecimalField(max_digits=9, decimal_places=3)
    subtotal: models.DecimalField(max_digits=9, decimal_places=3)
    Product_Discount = models.ForeignKey(Discounts , on_delete=models.CASCADE)


class PaymentTerm(models.Model):
    PAYMENTNAME = [
        ("Net 30","Net 30"),
        ("50 upfront","50 upfront"),
        ("COD","Cash on Delivery")
    ]


    name = models.CharField(max_length=255, choices=PAYMENTNAME)
    description = models.TextField()
    days_to_payment = models.DateField()
    percentage_due = models.DecimalField( max_digits=5, decimal_places=2)
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class PaymentSchedule(models.Model):
    INSTALLMENTS= [
        ("Pending","Pending"),
        ("Partially Paid","Partially Paid"),
        ("Paid","Paid"),
        ("Overdue","Overdue"),

    ]

    METHODS = [
        ("Credit Card","Credit Card"),
        ("Bank Transfer","Bank Transfer"),
        ("Cash","Cash"),
    ]
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.CASCADE)
    payment_status =  models.CharField(max_length=50, choices=INSTALLMENTS )
    percentage_of_total = models.DecimalField(max_digits=5, decimal_places=2)
    days_from_order = models.DateField()
    payment_due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=5, decimal_places=2)
    amount_paid = models.DecimalField( max_digits=5, decimal_places=2)
    payment_method =  models.CharField(max_length=50, choices=METHODS )
    payment_reference = models.CharField(max_length=255)
    notes = models.TextField() 
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)



class OrderPayment(models.Model):
    METHODS = [
        ("Credit Card","Credit Card"),
        ("Bank Transfer","Bank Transfer"),
        ("Cash","Cash"),
        ("Cheque","Cheque"),
    ]
    STATUS = [
        ("Completed","Completed"),
        ("Pending","Pending"),
        ("Failed","Failed"),
        ("Refunded","Refunded"),
    ]

    CURRENCY = [
        ("USD","USD"),
        ("INR","INR"),
        ("EUR","EUR"),
    ]
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE )
    amount_paid= models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateField(auto_now=True)
    payment_method = models.CharField(max_length=50, choices=METHODS)
    payment_reference = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices= STATUS)
    currency = models.CharField(max_length=255, choices= CURRENCY)                          
    created_by = models.ForeignKey(StoreManager, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


