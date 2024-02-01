from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)


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
    
from django.utils.text import slugify

class Color(models.Model):
    color_name = models.CharField(primary_key = True, max_length=255)

    slug = models.SlugField(unique= True)

    def save(self,  *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.color_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.color_name

class ProductImage(models.Model):

    IMAGE_TYPE = [
        ("Main Image","Main Image"),
        ("White Background", 'White Background'),
        ("Model Image", 'Model Image'),
        ("Catalogue Image","Catalogue Image"),
    ]
    Image_ID = models.IntegerField()
    Product = models.ForeignKey('Product', on_delete = models.CASCADE, null=True , related_name='images')
    Image = models.ImageField(upload_to ='product/images', null=True , blank=True)
    Image_type = models.CharField(max_length = 100,choices = IMAGE_TYPE, null=True, blank=True)
    Order_by = models.IntegerField(null=True, blank=True)
    Image_Uploaded_at = models.DateTimeField(auto_now=True)
    Image_Modified_at = models.DateTimeField(auto_now_add=True)

    # Uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # Modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class Product(models.Model):
    BRAND_CHOICES = [
        ("Cosmus", 'Cosmus'),
        ('Killer','Killer'),
        ("Tuffgear", 'Tuffgear'),
        ("BeeArmour", 'BeeArmour'),
        ("INIT","INIT"),
        ("OEM","OEM"),
    ]

    PRODUCT_STATUS = [
        ("Preproduction", 'Preproduction'),
        ("Active", 'Active'),
        ("Inactive", 'Inactive'),
        ("Discontinued","Discontinued"),

    ]

    PRODUCT_CHANNEL = [
          ("Ecommerce", 'Ecommerce'),
          ("Retail", 'Retail'),
          ("Corporate", 'Corporate'),
          ("Modern Trade"," Modern Trade"),
          ("Export"," Export"),

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

        ("6 Months","6 Months"),
        ("12 Months","12 Months"),
        ("18 Months","18 Months"),
        ("24 Months","24 Months"),
        ("30 Months","30 Months"),
        ("36 Months","36 Months"),
        ("42 Months","42 Months"),
        ("48 Months","48 Months"),
        ("54 Months","54 Months"),
        ("60 Months","60 Months"),
    ]

    PRODUCT_GENDER = [

        ("Male","Male"),
        ("Female","Female"),
        ("Unisex","Unisex"),

    ]

    Product_Name = models.CharField(max_length=255, null = True, blank = True)
    Model_Name = models.CharField(max_length=255, null = True, blank = True)
    Product_ShortName = models.CharField(max_length=255, null=True, blank = True)
    Product_Brand = models.CharField(max_length=200, choices= BRAND_CHOICES , null=True, blank = True)
    Product_Status= models.CharField(max_length=255, choices= PRODUCT_STATUS, null = True, blank = True)
    Product_Channel= MultiSelectField(max_length=100 , choices = PRODUCT_CHANNEL ,null=True  , blank = True )
    Product_EANCode= models.CharField(max_length=255,  null=True, blank = True)
    Product_Refrence_ID = models.PositiveIntegerField(unique = True, blank = False, null = False)
    Product_Compartments=  models.CharField(max_length=50, choices= PRODUCT_COMPARTMENTS, null=True, blank = True)
    Product_UOM = models.CharField(max_length=50, choices =PRODUCT_UCOM , null=True, blank = True)
    Product_Accessory_Compartments= models.CharField(max_length=6, choices= PRODUCT_ACCESSORY_COMPARTMENTS, null=True, blank = True)
    Product_CapacityLtrs= models.PositiveIntegerField(null = True , blank = True)
    Product_Material= models.CharField(max_length=100,choices = PRODUCT_MATERIAL,  null=True, blank = True)
    Product_BulletPoint1= models.CharField(max_length=255,  null=True, blank = True)
    Product_BulletPoint2= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint3= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint4= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint5= models.CharField(max_length=255, null=True, blank = True)
    Product_ShortDescription= models.CharField(max_length=255, null=True, blank = True)
    Product_LongDescription= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WP_Length= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WP_Width= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WP_Height= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WP_Weight= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WOP_Length= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WOP_Width= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WOP_Height= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WOP_Weight= models.CharField(max_length=255, null=True, blank = True)
    Product_Cost_price = models.DecimalField(null= True, max_digits=10, decimal_places=2, blank = True)
    Product_MRP = models.DecimalField(null = True,max_digits=10, decimal_places=2, blank = True)
    Product_SalePrice_CustomerPrice= models.DecimalField(null = True,max_digits=10, decimal_places=2, blank = True)
    Product_BulkPrice=models.DecimalField(null = True,max_digits=10, decimal_places=2, blank = True)
    Product_WRP=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_CashCounterPrice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_CashCounterPrice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_CashCounterPrice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_IndiaMartPrice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_Retailer_dealer_Price=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_Wholesaler_DistributorPrice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank = True)
    Product_Video_URL= models.CharField(max_length=255, null=True, blank = True)
    Product_ProductionQty= models.IntegerField(null=True, blank = True)
    Product_ReadyStockFactoryQty=models.IntegerField(null=True, blank = True)
    Product_MotherWarehouseQty=models.IntegerField(null=True, blank = True)
    Product_WarehouseQty=models.IntegerField(null=True, blank = True)
    Product_RetailStoreQty=models.IntegerField(null=True, blank = True)
    Product_ManufacturingDate=models.DateField(auto_now_add=True, blank = True)
    Product_WarrantyCode= models.CharField(max_length=255,null=True, blank = True)
    Product_WarrantyTime= models.CharField(null = True,max_length=15, choices=WARRANTY_TIME, blank = True)
    Product_Gender= models.CharField(max_length=15, choices= PRODUCT_GENDER,null=True, blank = True)
    Product_Rating = models.FloatField(null=True, blank = True)
    color_primary = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, related_name='primary_color', blank = True)
    color_secondary = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, related_name='secondary_color', blank = True)
    color_tertiary = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, related_name='tertiary_color', blank = True)
    Product_HSNCode = models.IntegerField(default = '12345678', blank = True)
    Amazon_Link = models.URLField(max_length = 200, null=True, blank = True)
    Flipkart_Link = models.URLField(max_length = 200, null=True, blank = True) 
    Cosmus_link = models.URLField(max_length = 200, null=True, blank = True) 
    Youtube_Link = models.URLField(max_length = 200, null=True, blank = True)
    Product_GST = models.CharField(null = True,choices = PRODUCT_GST, max_length = 200, blank = True)
    Product_QtyPerBox = models.IntegerField(null=True, blank = True)

    


class PProduct_Creation(models.Model):
    Product = models.ForeignKey(Product, on_delete = models.CASCADE , related_name='productdetails')  
    PProduct_image = models.ImageField(upload_to ='pproduct/images',null=True , blank=True)
    PProduct_color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, related_name='production_primary_color')
    PProduct_SKU = models.IntegerField(primary_key = True)



class item_name(models.Model):
    Item_name = models.CharField(primary_key = True, max_length = 255)
    slug = models.SlugField(unique = True)

    def save(self,  *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.Item_name)
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.Item_name   

class Fabric_Group_Model(models.Model):
    fab_grp_name = models.CharField(primary_key = True, max_length = 255)
    slug = models.SlugField(unique = True)
    def save(self,  *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.fab_grp_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.fab_grp_name     

class Unit_Name_Create(models.Model):
    unit_name = models.CharField(primary_key = True, max_length= 255)
    slug = models.SlugField(unique = True)

    def save(self,  *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.unit_name)
        super().save(*args, **kwargs)


class Item_Creation(models.Model):
    STATUS =  [

        ("Unused","Unused"),
        ("Used","Used"),
        ("Slow Moving","Slow Moving"),
        ("Dead","Dead"),
        ]
    
    PACKING = [

        ("Roll","Roll"),
        ("Bundle","Bundle")]
    
    
    FandNFB = [

        ("Fabric","Fabric"),
        ("Non Fabric","Non Fabric"),
        ]
    
    FINISHES = [
        ("PVC Coating","PVC Coating"),
        ("PU Coating","PU Coating"),
        ("Black Nickle","Black Nickle"),
        ("polypropylene(PP)","polypropylene(PP)"),
    ]

    GST = [
        ("0%", '0%'),
        ("5%", '5%'),
        ("12%", '12%'),
        ("18%","18%"),
        ("28%","28"),

    ]
    #need to add many to many field to vendor 
    Description = models.CharField(unique= True, null=False, max_length = 255) 
    Name = models.ForeignKey(item_name, on_delete=models.PROTECT)
    Material_code = models.CharField(max_length = 255, null = True)
    Item_Color = models.ForeignKey(Color, on_delete=models.PROTECT, null=False, related_name='ItemColor')
    Packing = models.CharField(max_length = 255, choices = PACKING)
    unit_name_item = models.ForeignKey(Unit_Name_Create, on_delete = models.PROTECT, null=False) 
    Units = models.DecimalField(max_digits=10, decimal_places=2)
    Panha = models.DecimalField(max_digits=10, decimal_places=2)
    Fabric_nonfabric = models.CharField(max_length = 255, choices = FandNFB)
    Fabric_Finishes =  models.CharField(max_length = 255, choices = FINISHES)
    Fabric_Group = models.ForeignKey(Fabric_Group_Model, on_delete= models.PROTECT)
    GST = models.CharField(max_length = 255,choices=GST)
    HSN_Code = models.IntegerField()
    status= models.CharField(max_length=50, choices= STATUS)



# @receiver(pre_save, sender=Item_Creation)
# def update_combined_field(sender, instance, **kwargs):
#     # Combine the values of field1 and field2 and save it to combined_field
#     instance.Description = f"{instance.Fabric_Group} - {instance.Name} - {instance.Item_Color}"

    """
        or 
            def clean(self):
        cleaned_data = super().clean()
        # Get values from the three fields
        value1 = cleaned_data.get('field1')
        value2 = cleaned_data.get('field2')
        value3 = cleaned_data.get('field3')

        # Perform logic to autofill the autofill_field
        if value1 and value2 and value3:
            autofill_value = f'{value1}-{value2}-{value3}'
            cleaned_data['autofill_field'] = autofill_value

        return cleaned_data

    """



