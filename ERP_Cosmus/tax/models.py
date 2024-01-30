from django.db import models
from product.models import Product
from inventory.models import InventoryLocation

class TaxCategory(models.Model):
    TAX_NAME = [
        ("GST","GST"),
        ("VAT","VAT"),
        ("Sales Tax","Sales Tax"),
    ]
    Name = models.CharField(max_length=100 , choices=TAX_NAME)
    Description = models.TextField()





class TaxRate(models.Model):
    tax_category = models.ForeignKey(TaxCategory, on_delete= models.CASCADE)
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    effective_from = models.DateField()
    effective_to= models.DateField()
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    description = models.TextField()


class ProductTax(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.CASCADE)


class TaxCalculate(models.Model):
	# transaction = foreign key to transaction table  will link to ordertable 
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	tax_rate = models.ForeignKey(TaxRate, on_delete=models.CASCADE)
	tax_amount: models.DecimalField(max_digits=5, decimal_places=2)
    #base rate

class TaxExemption(models.Model):
    entity_type = models.CharField(max_length=255)
    entity_id = models.IntegerField()
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.CASCADE)
    reason = models.TextField()
    effective_from = models.DateField()
    effective_to= models.DateField()
