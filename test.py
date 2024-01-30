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


class MainCategory(models.Model):
    category_name = models.CharField(max_length = 250)
    parent = models.IntegerField() 

    def __str__(self):
        return self.category_name   


class Product2Category(models.Model):
    Product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    Category_id = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.Category_id.category_name} --- {self.Product_id.Product_Name}'


class ProductColor(models.model):
    color_name = models.CharField(max_length=255)



class Product(models.Model):
    BRAND_CHOICES = [
        ("Cosmus", 'Cosmus'),
        ("Tuffgear", 'Tuffgear'),
        ("BeeArmour", 'BeeArmour'),
        ("INIT","INIT"),
        ("Killer","Killer"),
    ]

    PRODUCT_STATUS = [
        ("Preproduction", 'Preproduction'),
        ("Active", 'Active'),
        ("Inactive", 'Inactive'),
        ("Discontinued","Discontinued"),

    ]

    PRODUCT_CHANNEL = [
        ("Online_Product", 'Online_Product'),
        ("Retail_Product", 'Retail_Product'),
        ("Corporate_Product", 'Corporate_Product'),
        (" Modern_Trade_Product"," Modern_Trade_Product"),
        ("Export_Product"," Export_Product"),

    ]

    PRODUCT_GST = [
        ("0%", '0%'),
        ("5%", '5%'),
        ("12%", '12%'),
        ("18%","18%"),
        ("28%","28"),

    ]

    PRODUCT_UCOM = [
        ("Pcs","Pcs"),
        ("Set of 3","Set of 3"),
    ]

    PRODUCT_COMPARTMENTS =[
        ("One","One"),
        ("Two","Two"),
        ("Three","Three"),
        ("Four","Four"),
        ("Five","Five"),
        ("Six","Six"),
        ("Seven","Seven"),
        ("Eight","Eight"),
        ("Nine","Nine"),
        ("Ten","Ten"),

    ]

    PRODUCT_ACCESSORY_COMPARTMENTS= [
        ("One","One"),
        ("Two","Two"),
        ("Three","Three"),
        ("Four","Four"),
        ("Five","Five"),
        ("Six","Six"),
        ("Seven","Seven"),
        ("Eight","Eight"),
        ("Nine","Nine"),
        ("Ten","Ten"),
        ]
    
    PRODUCT_MATERIAL = [
        ("PU Coated Polyester","PU Coated Polyester"),
        ("PU Coated Nylon","PU Coated Nylon"),
        ("Vegan Leather","Vegan Leather"),
        ("Polycarbonate","Polycarbonate"),
        ("Eva Shell","Eva Shell"),
        ("Cotton","Cotton"),
        ("Jute","Jute"),
        ]
    
    WARRANTY_TIME = [

        ("6 Month","6 Month"),
        ("12 Month","12 Month"),
        ("18 Month","18 Month"),
        ("24 Month","24 Month"),
        ("30 Month","30 Month"),
        ("36 Month","36 Month"),
        ("42 Month","42 Month"),
        ("48 Month","48 Month"),
        ("54 Month","54 Month"),
        ("60 Month","60 Month"),
    ]

    PRODUCT_GENDER = [

        ("Male","Male"),
        ("Female","Female"),
        ("Unisex","Unisex"),

    ]


    Product_Name = models.CharField(max_length=255)
    Product_ShortName = models.CharField(max_length=255)
    Product_Brand = models.CharField(max_length=15, choices= BRAND_CHOICES )
    Product_Status= models.CharField(max_length=15, choices= PRODUCT_STATUS)
    Product_Channel= models.CharField(max_length=23, choices= PRODUCT_CHANNEL)
    Product_EANCode= models.CharField(max_length=255)
    Product_SKU= models.PositiveIntegerField()
    Product_ModelName= models.CharField(max_length=255)
    Product_Compartments=  models.CharField(max_length=15, choices= PRODUCT_COMPARTMENTS)
    Product_UOM = models.CharField(max_length=50, choices =PRODUCT_UCOM )
    Product_Accessory_Compartments= models.CharField(max_length=6, choices= PRODUCT_ACCESSORY_COMPARTMENTS)
    Product_CapacityLtrs= models.PositiveIntegerField()
    Product_Material= models.CharField(max_length=20,choices = PRODUCT_MATERIAL)
    Product_BulletPoint1= models.CharField(max_length=255)
    Product_BulletPoint2= models.CharField(max_length=255)
    Product_BulletPoint3= models.CharField(max_length=255)
    Product_BulletPoint4= models.CharField(max_length=255)
    Product_BulletPoint5= models.CharField(max_length=255)
    Product_ShortDescription= models.CharField(max_length=255)
    Product_LongDescription= models.CharField(max_length=255)
    Product_Dimensions_WP_Length= models.CharField(max_length=255)
    Product_Dimensions_WP_Width= models.CharField(max_length=255)
    Product_Dimensions_WP_Height= models.CharField(max_length=255)
    Product_Dimensions_WP_Weight= models.CharField(max_length=255)
    Product_Dimensions_WOP_Length= models.CharField(max_length=255)
    Product_Dimensions_WOP_Width= models.CharField(max_length=255)
    Product_Dimensions_WOP_Height= models.CharField(max_length=255)
    Product_Dimensions_WOP_Weight= models.CharField(max_length=255)
    Product_MRP = models.DecimalField(max_digits=6, decimal_places=2)
    Product_SalePrice_CustomerPrice= models.DecimalField(max_digits=6, decimal_places=2)
    Product_BulkPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_OfflineOfferPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_CashCounterPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_IndiaMartPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_RetailerPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_RetailDistributorPrice=models.DecimalField(max_digits=6, decimal_places=2)
    Product_Video_URL= models.CharField(max_length=255)
    Product_ProductionQty= models.IntegerField()
    Product_ReadyStockFactoryQty=models.IntegerField()
    Product_MotherWarehouseQty=models.IntegerField()
    Product_WarehouseQty=models.IntegerField()
    Product_RetailStoreQty=models.IntegerField()
    Product_ManufacturingDate=models.DateField(auto_now_add=True)
    Product_WarrantyCode= models.CharField(max_length=255)
    Product_WarrantyTime= models.CharField(max_length=15, choices=WARRANTY_TIME)
    Product_Gender= models.CharField(max_length=15, choices= PRODUCT_GENDER)
    Product_Rating = models.FloatField()
    COLOR_PRIMARY = Product_color.objects.all().values_list('name', 'name')
    COLOR_TERTIARY = Product_color.objects.all().values_list('name', 'name')
    COLOR_SECONDARY = Product_color.objects.all().values_list('name', 'name')
    Colour_Primary = models.CharField(max_length=255 , choices= COLOR_PRIMARY)
    Colour_Secondary = models.CharField(max_length=255 , choices= COLOR_SECONDARY)
    Colour_Tertiary = models.CharField(max_length=255 , choices= COLOR_TERTIARY)
    Product_HSNCode = models.IntegerField()

    def __str__(self):
        return self.Product_Name
    

    




class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Image_MainImage = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG1 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG2 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG3 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG4 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG5 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG6 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG7 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG8 = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG_Dimensions = models.ImageField(upload_to ='inventory/images')
    Image_WhiteBG10_Accessories = models.ImageField(upload_to ='inventory/images')
    Image_Model_Image1 = models.ImageField(upload_to ='inventory/images')
    Image_Model_Image2 = models.ImageField(upload_to ='inventory/images')
    Image_Model_Image3 = models.ImageField(upload_to ='inventory/images')
    Image_Catalogue_Image = models.ImageField(upload_to ='inventory/images')
    Uploaded_at = models.DateTimeField(auto_now=True)
    Modified_at = models.DateTimeField(auto_now_add=True)
    # Uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')
    # Modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')

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
    location = models.ForeignKey('InventoryLocation', on_delete=models.CASCADE)
    description = models.TextField()


class ProductTax(models.Model):
    product = models.ForeignKey(Product , models.CASCADE)
    tax_rate = models.ForeignKey(TaxRate, models.CASCADE)


class TaxCalculate(models.Model):
	transaction = foreign key to transaction table  will link to ordertable 
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



class Barcode(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Product_Barcode = models.IntegerField()



class Vendor(models.Model):

    SERVICETYPE = [
        ("Product","Product"),
        ("Printing","Printing"),
        ("Logistics","Logistics"),

    ]

    name = models.CharField(max_length=255)
    contact_details =  models.CharField(max_length=255)
    address =  models.CharField(max_length=255)
    mobile_no =  models.CharField(max_length=255)
    GST = models.ForeignKey(Tax, models.CASCADE)
    Company_Name = models.CharField(max_length=255)
    Service_Type  =  models.CharField(choices=SERVICETYPE)
    Email_id = models.EmailField(max_length=254)
    description = models.TextField()



class InventoryLocation(models.Model):

    STORECHOICES = [
        ("COCO","Compay Owned Company Operated"),
        ("FOCO","Company Owned Franchisee Operated"),
        ("COFO","Franchisee Owned Company Operated"),
        ("FOFO","Franchisee Owned Franchisee Operated"),]
    
    PROPERTYTYPE = [
        ("Rented","Rented"),
        ("Shop in Shop","Shop in Shop"),
    ]

    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    Store_type =  models.CharField(choices=STORECHOICES)
    property_type = models.CharField(choices=PROPERTYTYPE)  
    discount = models.ForeignKey(Discounts , on_delete=models.CASCADE)  

class CurrentStock(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    quantity =  models.IntegerField()
    last_updated = models.DateTimeField()



class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    quantity = models.IntegerField()
    source_location: models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    destination_location: models.CharField(max_length=255)
    movement_date = models.DateTimeField()
    notes = models.TextField()
    created_at =  models.DateTimeField(auto_add=True)
    updated_at = models.DateTimeField(auto_add_now=True)
    logistics = models.ForeignKey('Logistic', on_delete=models.CASCADE)



class Orders(models.Model):
    STATUS = [
        ("Pending","Pending"),
        ("Under_Production","Under_Production"),
        ("Quality Check","Quality Check"),
        ("Ready to Ship","Ready to Ship"),
        ("In Transit","InTransit"),
        ("Delivered","Delivered"),

    ]
    Customer_Name = models.CharField(max_length=50)#Foreign key to usertable 
    order_date = models.DateTimeField(auto_now=True)
    Items = models.ForeignKey('OrderItem' , on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS)
    total_amount = models.DecimalField(max_digits=9, decimal_places=3)
    discount =  models.ForeignKey(Discounts , on_delete=models.CASCADE)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    Stock_Movement = models.ForeignKey(StockMovement, on_delete=models.CASCADE)
    payment_term = models.ForeignKey('payment_term', on_delete=models.CASCADE)
    total_due = models.CharField(max_length=255)
    total_paid = models.CharField(max_length=255)
    balance_due = models.CharField(max_length=255)
    total_due = models.DecimalField(max_digits=5, decimal_places=2)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2)
    balance_due = models.DecimalField(max_digits=5, decimal_places=2)



class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product: models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity: models.IntegerChoices()
    unit_price: models.DecimalField(max_digits=9, decimal_places=3)
    subtotal: models.DecimalField(max_digits=9, decimal_places=3)
    Product_Discount = models.ForeignKey(Discounts , on_delete=models.CASCADE)



class StockAdjustments(models.Model):

    REASON = [
        ("Damaged Goods","Damaged Goods"),
        ("Inventory Reconciliation","Inventory Reconciliation"),
        ("Product Return","Product Return")
    ]

    product = models.ForeignKey(Product , on_delete= models.CASCADE)
    location = models.ForeignKey(InventoryLocation , on_delete= models.CASCADE)
    adjusted_quantity = models.IntegerField()
    reason = models.CharField(max_length=255, choices=REASON)
    #adjusted_by = user table
    date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)



    
class Logistics(models.Model):
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
        ("Stock Adjustment","Stock Adjustment")
        ("Return","Return")
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
    Expected_Cost = models.DecimalField()
    Actual_Cost  = models.DecimalField()




class Return(models.Model):
    RETURNSTATUS = [
        ("Pending","Pending"),
        ("'Received","'Received")
        ("Processed","Processed")
    ]
    status = models.CharField(max_length=50)
    logistics = models.ForeignKey(Logistics, on_delete=models.CASCADE)
    notes = models.TextField()
    return_status = models.CharField(choices=RETURNSTATUS, max_length=50)
    created_at =  models.DateTimeField(auto_add=True)
    updated_at = models.DateTimeField(auto_add_now=True)
    return_date =  models.DateTimeField()
    return_reason = models.CharField( max_length=250)
    quantity = models.IntegerField()
    destination_location = models.CharField(max_length=255)
    source_location = models.CharField(max_length=255)
    return_reference = models.CharField()
    returnitems = models.ForeignKey('ReturnItems' , on_delete=models.CASCADE)

class ReturnItems(models.Model):
    return_id = models.IntegerField()
    product = models.ForeignKey( Product , on_delete=models.CASCADE)
    quantity = models.IntegerField()
    return_reason = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=255)
    notes = models.TextField()
    created_at =  models.DateTimeField(auto_add=True)
    updated_at = models.DateTimeField(auto_add_now=True)





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
    created_at =  models.DateTimeField(auto_add=True)
    updated_at = models.DateTimeField(auto_add_now=True)



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
    created_at =  models.DateTimeField(auto_add=True)
    updated_at = models.DateTimeField(auto_add_now=True)



class OrderPayment(models.Model):
    METHODS = [
        ("Credit Card","Credit Card"),
        ("Bank Transfer","Bank Transfer"),
        ("Cash","Cash"),
    ]

    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE )
    amount_paid= models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateField(auto_now=True)
    payment_method = models.CharField(max_length=50, choices=METHODS)


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