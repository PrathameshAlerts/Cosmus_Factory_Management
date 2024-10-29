from django.db import models
from order.models import Orders




class Logistic(models.Model):
    CARRIER = [
        ("UPS","UPS"),
        ("DTDC","DTDC"),
        ("Express Delivery","Express Delivery")
    ]

    STATUS = [
        ("In Transit","In Transit"),
        ("Delivered","Delivered"),
    ]

    TYPES = [
        ("Inbound","Inbound"),
        ("Outbound","Outbound"),
        ("Stock Adjustment","Stock Adjustment"),
        ("Return","Return"),
    ]

    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    shipment_date = models.DateField(auto_now=True)
    movement_type = models.CharField(max_length=50, choices= TYPES)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField()
    tracking_number = models.IntegerField()
    carrier = models.CharField(max_length=50, choices=CARRIER)
    status = models.CharField(max_length=50, choices= STATUS)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    Expected_Cost = models.DecimalField(max_digits=10, decimal_places=2)
    Actual_Cost  = models.DecimalField(max_digits=10, decimal_places=2)
