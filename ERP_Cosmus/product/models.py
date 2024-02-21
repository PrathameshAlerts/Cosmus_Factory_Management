from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_save


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
    

class Color(models.Model):
    color_name = models.CharField( max_length=255, unique= True, null = False, blank = False)
    def __str__(self):
        return self.color_name
    
class gst(models.Model):
    gst_percentage = models.CharField(max_length = 50)


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
        ('0 Months','0 Months'),
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

    Product_Name = models.CharField(max_length=255,  blank = True)
    Model_Name = models.CharField(max_length=255, blank = True)
    Product_ShortName = models.CharField(max_length=200, null=True, blank = True)
    Product_Brand = models.CharField(max_length=200, choices= BRAND_CHOICES , blank = True, default = "Cosmus")
    Product_Status= models.CharField(max_length=100, choices= PRODUCT_STATUS,  blank = True, default = "Active")
    Product_Channel= MultiSelectField(max_length=100 , choices = PRODUCT_CHANNEL ,null=True  , blank = True )
    Product_EANCode= models.CharField(max_length=100,  null=True, blank = True)
    Product_Refrence_ID = models.PositiveIntegerField(unique = True, blank = False, null = False)
    Product_Compartments=  models.CharField(max_length=50, choices= PRODUCT_COMPARTMENTS, null=True, blank = True)
    Product_UOM = models.CharField(max_length=50, choices =PRODUCT_UCOM , null=True, blank = True)
    Product_Accessory_Compartments= models.CharField(max_length=20, choices= PRODUCT_ACCESSORY_COMPARTMENTS, null=True, blank = True)
    Product_CapacityLtrs= models.PositiveIntegerField(null = True , blank = True)
    Product_Material= models.CharField(max_length=100,choices = PRODUCT_MATERIAL,  null=True, blank = True)
    Product_BulletPoint1= models.CharField(max_length=255,  null=True, blank = True)
    Product_BulletPoint2= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint3= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint4= models.CharField(max_length=255, null=True, blank = True)
    Product_BulletPoint5= models.CharField(max_length=255, null=True, blank = True)
    Product_ShortDescription= models.CharField(max_length=255, null=True, blank = True)
    Product_LongDescription= models.CharField(max_length=255, null=True, blank = True)
    Product_Dimensions_WP_Length= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WP_Width= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WP_Height= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WP_Weight= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WOP_Length= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WOP_Width= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WOP_Height= models.CharField(max_length=150, null=True, blank = True)
    Product_Dimensions_WOP_Weight= models.CharField(max_length=150, null=True, blank = True)
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
    Product_WarrantyCode= models.CharField(max_length=150,null=True, blank = True)
    Product_WarrantyTime= models.CharField(max_length=15, choices=WARRANTY_TIME, blank = True, default = '0 Months')
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
    Product_GST = models.ForeignKey(gst, blank = True, on_delete = models.PROTECT, default = 1)
    Product_QtyPerBox = models.IntegerField(null=True, blank = True)

 
    def P_GST(self):
        return self.Product_GST.gst_percentage
    

class PProduct_Creation(models.Model):
    Product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='productdetails')  
    PProduct_image = models.ImageField(upload_to ='pproduct/images' ,null=True ,blank=True)
    PProduct_color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, related_name='production_primary_color')
    PProduct_SKU = models.IntegerField(primary_key = True)

    def product_color_name(self):
        return self.PProduct_color.color_name
     

class Fabric_Group_Model(models.Model):
    fab_grp_name = models.CharField(max_length=255,unique= True, null = False, blank = False)


class Unit_Name_Create(models.Model):
    unit_name = models.CharField( max_length=255,unique= True, null = False, blank = False)



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


    #need to add many to many field to vendor 
    item_name = models.CharField(unique= True, null=False, max_length = 255)
    Material_code = models.CharField(max_length = 255)
    Item_Color = models.ForeignKey(Color, on_delete=models.PROTECT, null=False, related_name='ItemColor')
    Packing = models.CharField(max_length = 255, choices = PACKING)
    unit_name_item = models.ForeignKey(Unit_Name_Create, on_delete = models.PROTECT, null=False) 
    Units = models.DecimalField(max_digits=10, decimal_places=2)
    Panha = models.DecimalField(max_digits=10, decimal_places=2)
    Fabric_nonfabric = models.CharField(max_length = 255, choices = FandNFB)
    Fabric_Finishes =  models.CharField(max_length = 255, choices = FINISHES)
    Fabric_Group = models.ForeignKey(Fabric_Group_Model, on_delete= models.PROTECT)
    Item_Creation_GST = models.ForeignKey(gst, on_delete = models.PROTECT)
    HSN_Code = models.CharField(max_length = 100, blank = True)
    status= models.CharField(max_length=50, choices= STATUS)
    item_shade_image = models.ImageField(upload_to = 'rawmaterial/images', null=True , blank=True)

# these functions are used to show related attributes instead of PK id in listview
   
    def Color_Name(self):
        return self.Item_Color.color_name

    def fab_grp(self):
        return self.Fabric_Group.fab_grp_name
    

    def Unit_Name(self):
        return self.unit_name_item.unit_name


    def Item_GST(self):
        return self.Item_Creation_GST.gst_percentage

class item_color_shade(models.Model):
    items = models.ForeignKey(Item_Creation, on_delete = models.CASCADE, related_name = 'shades')
    item_name_rank = models.PositiveIntegerField(null = True, blank = True)
    item_shade_name =  models.CharField(max_length=100, null = True, blank = True)
    item_color_image = models.ImageField(upload_to ='rawmaterial/images', null=True , blank=True)




#post_save signal for item_color_shade if Item_Creation instance is created 
@receiver(post_save, sender=Item_Creation)
def save_primary_item_color_shade(sender, instance, created, **kwargs): #instance is the created instance of Item_Creation
    if created:
        #getting the color name attribte instead of object function
        color_name = instance.Item_Color.color_name
        # Create a new item_color_shade object related to the newly created instance
        primary_color_shade = item_color_shade.objects.create(items=instance,  # Assign the instance itself, not just the primary key
                                                            item_name_rank= 1,
                                                            item_shade_name = color_name,
                                                            item_color_image = instance.item_shade_image)
        # Save the newly created item_color_shade object
        primary_color_shade.save()




class AccountGroup(models.Model):
    account_group = models.CharField(max_length = 50 , unique= True)



class AccountSubGroup(models.Model):
    acc_grp = models.ForeignKey(AccountGroup, on_delete = models.PROTECT)
    account_sub_group = models.CharField(max_length = 50, unique= True)

    def account_main_group(self):
        return self.acc_grp.account_group


class StockItem(models.Model):
    acc_sub_grp = models.ForeignKey(AccountSubGroup, on_delete = models.PROTECT)
    stock_item_name = models.CharField(max_length= 150 ,unique= True)

    def account_sub_group(self):
        return self.acc_sub_grp.account_sub_group
    

class Ledger(models.Model):
    MAINTAIN_BILLWISE = [
        ("Yes", 'Yes'),
        ("No", 'No'),
    ]

    MAINTAIN_BILLWISE = [
        ("Trader", 'Trader'),
        ("Manufacture", 'Manufacture'),
    ]

    DEBIT_CREDIT = [
        ("Debit", 'Debit'),
        ("Credit", 'Credit'),
    ]

    name = models.CharField(max_length = 100, blank = True)
    short_name = models.CharField(max_length = 100, null= True,blank = True)
    vendor_code = models.CharField(max_length = 100, null= True,blank = True)
    under_group  = models.ForeignKey(AccountSubGroup, on_delete = models.PROTECT)
    maintain_billwise = models.CharField(choices = MAINTAIN_BILLWISE, max_length = 30, blank = True)
    default_credit_period = models.CharField(max_length = 100, blank = True)
    types = models.CharField(choices = MAINTAIN_BILLWISE , max_length = 30, blank = True)
    Gst_no = models.CharField(max_length = 100, blank = True)
    date = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length = 255, blank = True)
    state = models.CharField(max_length = 255, blank = True)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True) 
    pincode = models.IntegerField()
    mobile_no = models.IntegerField()
    landline_no = models.IntegerField()
    bank_details =  models.CharField(max_length = 255, blank = True)
    Debit_Credit =  models.CharField( choices = DEBIT_CREDIT ,max_length = 255, blank = True)










































# @receiver(pre_save, sender=Item_Creation)
# def update_combined_field(sender, instance, **kwargs):
#     # Combine the values of field1 and field2 and save it to combined_field
#     instance.Description = f"{instance.Fabric_Group} - {instance.Name} - {instance.Item_Color}"

    """
        or in forms
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



