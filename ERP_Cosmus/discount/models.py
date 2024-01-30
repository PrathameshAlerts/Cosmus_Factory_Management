from django.db import models

class Discounts(models.Model):
    TYPE = [
        ("Percentage","Percentage"),
        ("Fixed Amount","Fixed Amount"),
    ]
    discount_type = models.CharField(choices=TYPE, max_length=50)
    discount_value = models.IntegerField()
    start_date = models.DateField()
    end_date  = models.DateField() 
    notes= models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)