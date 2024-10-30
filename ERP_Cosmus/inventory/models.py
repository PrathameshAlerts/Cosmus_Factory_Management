from django.db import models
from discount.models import Discounts
from order.models import StoreManager, Orders
from product.models import Product
from logistics.models import Logistic

class Barcode(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Product_Barcode = models.IntegerField()


class Vendor(models.Model):

    SERVICETYPE = [
        ("Product", "Product"),
        ("Printing", "Printing"),
        ("Logistic", "Logistic"),
    ]

    name = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=255)
    GST = models.CharField(max_length=30)
    Company_Name = models.CharField(max_length=255)
    Service_Type = models.CharField(choices=SERVICETYPE,max_length=254)
    Email_id = models.EmailField(max_length=254)
    description = models.TextField()


class InventoryLocation(models.Model):

    STORECHOICES = [
        ("COCO", "Compay Owned Company Operated"),
        ("FOCO", "Company Owned Franchisee Operated"),
        ("COFO", "Franchisee Owned Company Operated"),
        ("FOFO", "Franchisee Owned Franchisee Operated"),
    ]

    PROPERTYTYPE = [
        ("Rented", "Rented"),
        ("Shop in Shop", "Shop in Shop"),
    ]

    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    Store_type = models.CharField(max_length=255,choices=STORECHOICES)
    property_type = models.CharField(max_length=255,choices=PROPERTYTYPE)
    discount = models.ForeignKey(Discounts, on_delete=models.CASCADE)


class CurrentStock(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField()


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    source_location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    destination_location = models.CharField(max_length=255)
    movement_date = models.DateTimeField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    logistic = models.ForeignKey(Logistic, on_delete=models.CASCADE)


class StockAdjustments(models.Model):

    REASON = [
        ("Damaged Goods", "Damaged Goods"),
        ("Inventory Reconciliation", "Inventory Reconciliation"),
        ("Product Return", "Product Return"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    adjusted_quantity = models.IntegerField()
    reason = models.CharField(max_length=255, choices=REASON)
    user = models.ForeignKey(StoreManager, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)

















"""
Discounts
MainCategory
Product2Category
ProductColor
Product
ProductImage
TaxCategory
TaxRate
ProductTax
TaxCalculate
TaxExemption
Barcode
Vendor
InventoryLocation
CurrentStock
StockMovement
Orders
OrderItem
StockAdjustments
Logistics
Return
ReturnItems
PaymentTerm
PaymentSchedule
OrderPayment

"""