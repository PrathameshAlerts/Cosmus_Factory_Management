from django.db import models
from logistics.models import Logistic
from product.models import Product

class ReturnItems(models.Model):
    return_id = models.IntegerField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    return_reason = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=255)
    notes = models.TextField()
    created_at =  models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Return(models.Model):
    RETURNSTATUS = [
        ("Pending","Pending"),
        ("'Received","'Received"),
        ("Processed","Processed"),
    ]
    status = models.CharField(max_length=50)
    logistics = models.ForeignKey(Logistic, on_delete=models.CASCADE)
    notes = models.TextField()
    return_status = models.CharField(choices=RETURNSTATUS, max_length=50)
    created_at =  models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    return_date =  models.DateTimeField()
    return_reason = models.CharField( max_length=250)
    quantity = models.IntegerField()
    destination_location = models.CharField(max_length=255)
    source_location = models.CharField(max_length=255)
    return_reference = models.CharField(max_length = 200)
    returnitems = models.ForeignKey(ReturnItems , on_delete=models.CASCADE)

