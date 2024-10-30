
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from multiselectfield import MultiSelectField
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator

from core.models import Company


CustomUserModel = settings.AUTH_USER_MODEL
DECIMAL_PLACE_CONSTANT = 3



class CompanyBaseModel(models.Model):
    """
    An abstract base model to be inherited by all models that need company-level isolation.
    """
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null = True, blank=True)
    
    class Meta:
        abstract = True  # This will be used as an abstract base class

    def save(self, *args, **kwargs):
        # Check if the user is not a superuser
        if self.c_user and not self.c_user.is_superuser:
            # Automatically assign company if it's not already set and the user has a company (failsafe option)
            if not self.company:
                self.company = self.c_user.company

        # company for superusers is set from frontend dropdown menu directly and password to form variables
        # Ensure company is assigned before saving, even for superusers
        if not self.company:
            raise ValidationError('Company must be specified.')

        super().save(*args, **kwargs)


class MainCategory(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    product_category_name = models.CharField(max_length = 250, unique = True)

    def __str__(self):
        return self.product_category_name   


class SubCategory(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    product_sub_category_name = models.CharField(max_length = 250)
    product_main_category = models.ForeignKey(MainCategory, on_delete = models.PROTECT, related_name = 'subcategories')

    # class Meta:
    #     unique_together = [['product_sub_category_name','product_main_category']]

    def __str__(self):
        return self.product_sub_category_name 


class Product2SubCategory(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, null=True, blank=True)
    Product_id = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='product_cats')
    SubCategory_id = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name='subcategories')

    # def validate_unique(self, exclude=None):
    #     if self.Product_id and self.SubCategory_id:
    #         queryset = Product2SubCategory.objects.filter(
    #             Product_id = self.Product_id,
    #             SubCategory_id__product_main_category=self.SubCategory_id.product_main_category)
    #         if queryset.exists() and not self.pk:
    #             raise ValidationError(
    #                 {'Product_id': 'This combination already exists for the same main category.'}
    #             )

    class Meta:
        unique_together = [['Product_id','SubCategory_id']]
    
    def __str__(self):  
        return f'{self.SubCategory_id.product_sub_category_name} --- {self.Product_id.Product_Name}'
    

class Color(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    color_name = models.CharField(max_length=255, unique= True, null = False, blank = False)
    
    class Meta:
        ordering = ["color_name"]

    def __str__(self):
        return self.color_name
    
    
class gst(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    gst_percentage = models.IntegerField(unique=True)
    class Meta:
        ordering = ["gst_percentage"]


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

    PRODUCT_MATERIAL = [
        ("PU Coated Polyester","PU Coated Polyester"),
        ("PU Coated Nylon","PU Coated Nylon"),
        ("Vegan Leather","Vegan Leather"),
        ("Polycarbonate","Polycarbonate"),
        ("Eva Shell","Eva Shell"),
        ("Cotton","Cotton"),
        ("Jute","Jute"),
        ]

    PRODUCT_GENDER = [

        ("Male","Male"),
        ("Female","Female"),
        ("Unisex","Unisex"),

    ]

    PRODUCT_COMPARTMENTS = [
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

    PRODUCT_UCOM = [
        ("Pcs","Pcs"),
        ("Set of 3","Set of 3"),
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

    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT,null=True, blank=True)
    Product_Name = models.CharField(max_length=255, blank = True, null = True, unique=True)
    Model_Name = models.CharField(unique=True,max_length=255, blank = True ,null =True)
    Product_Brand = models.CharField(max_length=200, choices= BRAND_CHOICES , blank = True, null = True)
    Product_Status= models.CharField(max_length=100, choices= PRODUCT_STATUS,  blank = True, null = True)
    Product_Channel= MultiSelectField(max_length=100, choices = PRODUCT_CHANNEL , blank = True)
    Product_Refrence_ID = models.PositiveBigIntegerField(unique = True, blank = False,null =False)
    Product_Cost_price = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank = True, null = True)
    Product_MRP = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank = True, null = True)
    Product_SalePrice_CustomerPrice= models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank = True, null = True)
    Product_BulkPrice=models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank = True, null = True)
    Product_WarrantyTime= models.CharField(max_length=15, choices=WARRANTY_TIME, blank = True, null = True)
    Product_HSNCode = models.PositiveBigIntegerField(blank = True,null =True)
    Product_GST = models.ForeignKey(gst, blank = True, on_delete = models.PROTECT, null = True)
    Product_ShortName = models.CharField(max_length=200, blank = True, null =True)
    Product_Compartments=  models.CharField(max_length=50, choices= PRODUCT_COMPARTMENTS,  blank = True, null =True)
    Product_UOM = models.CharField(max_length=50, choices = PRODUCT_UCOM ,  blank = True,null =True)
    Product_Accessory_Compartments= models.CharField(max_length=20, choices = PRODUCT_ACCESSORY_COMPARTMENTS, null=True, blank = True)
    Product_CapacityLtrs = models.PositiveIntegerField(blank = True,null =True)
    Product_Material= models.CharField(max_length=100, choices = PRODUCT_MATERIAL, blank = True, null =True)
    Product_BulletPoint1= models.CharField(max_length=255, blank = True, null =True)
    Product_BulletPoint2= models.CharField(max_length=255, blank = True, null =True)
    Product_BulletPoint3= models.CharField(max_length=255,  blank = True, null =True)
    Product_BulletPoint4= models.CharField(max_length=255,  blank = True, null =True)
    Product_BulletPoint5= models.CharField(max_length=255, blank = True, null =True)
    Product_ShortDescription= models.CharField(max_length=255, blank = True,null =True)
    Product_LongDescription= models.CharField(max_length=255,  blank = True,null =True)
    Product_Dimensions_WP_Length= models.CharField(max_length=150,  blank = True,null =True)
    Product_Dimensions_WP_Width= models.CharField(max_length=150,  blank = True,null =True)
    Product_Dimensions_WP_Height= models.CharField(max_length=150,  blank = True,null =True)
    Product_Dimensions_WP_Weight= models.CharField(max_length=150,  blank = True,null =True)
    Product_Dimensions_WOP_Length= models.CharField(max_length=150,blank = True,null =True)
    Product_Dimensions_WOP_Width= models.CharField(max_length=150, blank = True,null =True)
    Product_Dimensions_WOP_Height= models.CharField(max_length=150,  blank = True,null =True)
    Product_Dimensions_WOP_Weight= models.CharField(max_length=150, blank = True,null =True)
    Product_WRP = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,  blank = True,null =True)
    Product_CashCounterPrice=models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,  blank = True,null =True)
    Product_IndiaMartPrice=models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank = True,null =True)
    Product_Retailer_dealer_Price=models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,  blank = True,null =True)
    Product_Wholesaler_DistributorPrice=models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,  blank = True,null =True)
    Product_Create_Date=models.DateField(auto_now=True)
    Product_Gender= models.CharField(max_length=15, choices= PRODUCT_GENDER, blank=True, null = True)
    Product_QtyPerBox = models.IntegerField(blank = True,null =True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)
    labour_charges = models.IntegerField(default=0)

    def P_GST(self):
        if self.Product_GST is not None:
            return self.Product_GST.gst_percentage
        else:
            return None  # or any default value you prefer


class PProduct_Creation(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT,null=True, blank=True)
    Product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='productdetails')  
    PProduct_image = models.ImageField(upload_to = 'pproduct/images',  blank=True)
    PProduct_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='production_primary_color')
    PProduct_SKU = models.PositiveBigIntegerField(primary_key = True)
    Product_EANCode = models.CharField(max_length=100, blank = True)
    Product_Rating = models.FloatField(blank = True, null = True)
    Amazon_Link = models.URLField(max_length = 200,  blank = True)
    Flipkart_Link = models.URLField(max_length = 200,  blank = True) 
    Cosmus_link = models.URLField(max_length = 200, blank = True) 
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)

    def product_color_name(self):
        return self.PProduct_color.color_name
     

class ProductImage(models.Model):

    IMAGE_TYPE = [
        ("Main Image","Main Image"),
        ("White Background", 'White Background'),
        ("Model Image", 'Model Image'),
        ("Catalogue Image","Catalogue Image"),
    ]

    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    Product = models.ForeignKey(PProduct_Creation, on_delete = models.CASCADE, related_name='productimages')
    Image = models.ImageField(upload_to ='product/images', blank=True)
    Image_type = models.CharField(max_length = 100, choices = IMAGE_TYPE, blank=True)
    Order_by = models.IntegerField(blank=True)
    Image_Uploaded_at = models.DateTimeField(auto_now=True)
    Image_Modified_at = models.DateTimeField(auto_now_add=True)


class Product_A_plus_content(models.Model):

    DIMENSIONS = [
        ('200 * 200','200 * 200'),
        ('1260 * 200','1260 * 200'),
        ('1080 * 720','1080 * 720'),
    ]
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    Product = models.ForeignKey(PProduct_Creation, on_delete = models.CASCADE, related_name='productaplus')
    heading = models.CharField(max_length = 255)
    details = models.TextField()
    orderby = models.IntegerField()
    images = models.ImageField(upload_to = 'pproduct/images',  blank=True)
    dimensions = models.CharField(max_length = 70, choices = DIMENSIONS)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class ProductVideoUrls(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    Product = models.ForeignKey(PProduct_Creation, on_delete = models.CASCADE, related_name='productvideourls')
    product_video_url =  models.URLField(max_length = 255, blank = True)
    Image_Uploaded_at = models.DateTimeField(auto_now=True)
    Image_Modified_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class Fabric_Group_Model(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    fab_grp_name = models.CharField(max_length=255,unique= True, null = False, blank = False)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)
    
    class Meta:
        ordering = ['fab_grp_name']

class Unit_Name_Create(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    unit_name = models.CharField(max_length=100,unique = True, null = False, blank = False)
    unit_value = models.CharField(max_length=100,null = False, blank = False)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)

    class Meta:
        ordering = ['unit_name']


class FabricFinishes(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    fabric_finish =  models.CharField(max_length = 100, unique=True)

    class Meta:
        ordering = ['fabric_finish']


class packaging(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT)
    packing_material = models.CharField(max_length = 100, unique=True)
    
    class Meta:
        ordering = ['packing_material']



class Item_Creation(models.Model):

    STATUS =  [
        ("Unused","Unused"),
        ("Used","Used"),
        ("Slow Moving","Slow Moving"),
        ("Dead","Dead"),
        ]

    FandNFB = [
        ("Fabric","Fabric"),
        ("Non Fabric","Non Fabric")]

    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, blank=True, null=True)
    item_name = models.CharField(unique = True, null=False, max_length = 255)
    Material_code = models.CharField(max_length = 255, unique=True, null=False, blank=False)
    Item_Color = models.ForeignKey(Color, on_delete=models.PROTECT, null=False, related_name='ItemColor')
    Item_Packing = models.ForeignKey(packaging, on_delete=models.PROTECT)
    unit_name_item = models.ForeignKey(Unit_Name_Create, on_delete = models.PROTECT, null=False) 
    Units = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,null=False, blank=False)
    Panha = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,null=False, blank=False)
    Fabric_nonfabric = models.CharField(max_length = 255, choices = FandNFB)
    Item_Fabric_Finishes = models.ForeignKey(FabricFinishes, on_delete = models.PROTECT)
    Fabric_Group = models.ForeignKey(Fabric_Group_Model,related_name='items' ,on_delete= models.PROTECT)
    Item_Creation_GST = models.ForeignKey(gst, on_delete = models.PROTECT)
    HSN_Code = models.CharField(max_length = 100, blank = True)
    status = models.CharField(max_length = 50, choices= STATUS)
    item_shade_image = models.ImageField(upload_to = 'rawmaterial/images', null=True , blank=True)
    created_date = models.DateTimeField(auto_now =True)
    modified_date_time = models.DateTimeField(auto_now_add = True)
    

    # these functions are used to show related attributes instead of PK id in listview
    def Color_Name(self):
        return self.Item_Color.color_name

    def fab_grp(self):
        return self.Fabric_Group.fab_grp_name
    
    def Unit_Name(self):
        return self.unit_name_item.unit_name


    def Item_GST(self):
        return self.Item_Creation_GST.gst_percentage
    
    def Fab_Finishes(self):
        return self.Item_Fabric_Finishes.fabric_finish
    
    def Packaging_Material(self):
        return self.Item_Packing.packing_material

    def __str__(self):
        return self.item_name
    

class item_color_shade(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, blank=True, null=True)
    items = models.ForeignKey(Item_Creation, on_delete = models.CASCADE, related_name = 'shades')
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,blank=True,default=0)
    item_name_rank = models.PositiveIntegerField(blank = True, null = True)
    item_shade_name =  models.CharField(max_length=100, null=False, blank=False)
    item_color_image = models.ImageField(upload_to ='rawmaterial/images') 
    created_date = models.DateTimeField(auto_now = True)
    modified_date_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = [['items','item_shade_name']]
        ordering = ['items__item_name']

    def __str__(self):
        return self.item_shade_name


class opening_shade_godown_quantity(models.Model):
    opening_purchase_voucher_godown_item = models.ForeignKey(item_color_shade, on_delete = models.CASCADE)
    opening_godown_id = models.ForeignKey('Godown_raw_material', on_delete = models.PROTECT)
    opening_quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    opening_rate = models.DecimalField(max_digits=10, decimal_places = DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now = True)
    modified_date_time = models.DateTimeField(auto_now_add = True)


class AccountGroup(models.Model):
    account_group = models.CharField(max_length = 50 , unique = True)


class AccountSubGroup(models.Model):
    acc_grp = models.ForeignKey(AccountGroup, on_delete = models.PROTECT)
    account_sub_group = models.CharField(max_length = 50, unique= True)

    def account_main_group(self):
        return self.acc_grp.account_group


class StockItem(CompanyBaseModel):
    acc_sub_grp = models.ForeignKey(AccountSubGroup, on_delete = models.PROTECT)
    stock_item_name = models.CharField(max_length= 150)
    created_date = models.DateTimeField(auto_now = True)
    modified_date_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = [['stock_item_name','company']]

    def account_sub_group(self):
        return self.acc_sub_grp.account_sub_group
    
    def save(self, *args, **kwargs):

        # Exclude current instance from the validation check
        existing_objects = StockItem.objects.exclude(id=self.id)
        if existing_objects.filter(stock_item_name__iexact = self.stock_item_name, company = self.company):
             raise ValidationError(f'{self.stock_item_name} already exists!')

        return super().save(*args, **kwargs)
    

class ledgerTypes(models.Model):
    type_name = models.CharField(unique=True, null=False, blank=False ,max_length=50)


class Ledger(models.Model):
    MAINTAIN_BILLWISE = [
        ("Yes", 'Yes'),
        ("No", 'No'),
    ]

    DEBIT_CREDIT = [
        ("Debit", 'Debit'),
        ("Credit", 'Credit'),
        ('N/A','N/A'),
    ]
    
    name = models.CharField(max_length = 100, blank = True, unique=True)
    short_name = models.CharField(max_length = 100, blank = True)
    vendor_code = models.CharField(max_length = 100, unique= True)
    under_group  = models.ForeignKey(AccountSubGroup, on_delete = models.PROTECT)
    maintain_billwise = models.CharField(choices = MAINTAIN_BILLWISE, max_length = 30, blank = True)
    default_credit_period = models.CharField(max_length = 100, blank = True)
    types = models.ForeignKey(ledgerTypes, blank=True, on_delete=models.PROTECT)
    Gst_no = models.CharField(max_length = 100, validators = [MinLengthValidator(15), MaxLengthValidator(15)])
    address = models.TextField(blank = True) 
    state = models.CharField(max_length = 255, blank = True)
    country = models.CharField(max_length = 255,  blank=True) 
    city = models.CharField(max_length = 255,  blank=True) 
    pincode = models.IntegerField()
    mobile_no = models.BigIntegerField()
    landline_no = models.BigIntegerField()
    bank_details =  models.TextField(blank = True)
    Debit_Credit =  models.CharField(choices = DEBIT_CREDIT ,max_length = 255, blank = True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)

    def account_sub_group_ledger(self):
        return self.under_group.account_sub_group



class account_credit_debit_master_table(models.Model):
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, blank = False, null = False, related_name = 'transaction_entry')
    debit = models.DecimalField(max_digits=12, decimal_places=DECIMAL_PLACE_CONSTANT, default = 0)
    credit = models.DecimalField(max_digits=12, decimal_places=DECIMAL_PLACE_CONSTANT, default = 0)
    voucher_no = models.CharField(null = True, blank= True)
    voucher_type = models.CharField(max_length = 100)
    particulars = models.CharField(max_length = 100)
    create_date = models.DateField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)



class Godown_raw_material(models.Model): # CompanyBaseModel
    godown_name_raw = models.CharField(max_length = 225, unique= True)

    class Meta:
        unique_together = [['godown_name_raw']] # ,'company'

    def __str__(self) -> str:
        return self.godown_name_raw      

    def save(self, *args, **kwargs):
        existing_objects = Godown_raw_material.objects.exclude(id = self.id)

        # if self.user.is_superuser:
        #     if existing_objects.filter(godown_name_raw__iexact = self.godown_name_raw).exists(): # ,company=self.company
        #         raise ValidationError(f'{self.godown_name_raw} already exists!')
        # else:
        if existing_objects.filter(godown_name_raw__iexact = self.godown_name_raw).exists(): # c_user__company=self.c_user.company
            raise ValidationError(f'{self.godown_name_raw} already exists!')

        super().save(*args, **kwargs)

class item_shades_godown_report(models.Model):  

    inward_outward = [
        ('inward', 'inward'),
        ("outward", 'outward'),
    ]

    item_shade_name = models.ForeignKey(item_color_shade, on_delete =models.PROTECT)
    create_date = models.DateField(auto_now = True)
    modified_date = models.DateField(auto_now_add = True)
    particulars = models.CharField(max_length = 150) 
    voucher_type = models.CharField(max_length = 150)
    voucher_no = models.IntegerField()
    inward_outward = models.CharField(max_length = 50, choices = inward_outward)
    Quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)



class Godown_finished_goods(models.Model):
    godown_name_finished = models.CharField(max_length = 225)


    class Meta:
        unique_together = [['godown_name_finished']]  # ,'company'

    def save(self,*args, **kwargs):
        existing_objects = Godown_finished_goods.objects.exclude(id=self.id)

        if existing_objects.filter(godown_name_finished__iexact = self.godown_name_finished).exists(): # c_user__company=self.c_user.company
            raise ValidationError(f'{self.godown_name_finished} already exists!')

        super().save(*args, **kwargs)




class product_godown_quantity_through_table(models.Model):
    godown_name = models.ForeignKey(Godown_finished_goods, on_delete = models.PROTECT, related_name= 'finished_godown_names')
    product_color_name = models.ForeignKey(PProduct_Creation, related_name = 'godown_colors', on_delete = models.PROTECT)
    quantity = models.BigIntegerField(default = 0)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)


    class Meta:
        unique_together = [['godown_name','product_color_name']]

    def __str__(self):
        return f'{self.godown_name}-{self.product_color_name} - {self.quantity}'



class RawStockTransferMaster(models.Model):
    voucher_no = models.IntegerField(primary_key=True)
    source_godown = models.ForeignKey(Godown_raw_material, on_delete=models.CASCADE , related_name='source_godowns')
    destination_godown = models.ForeignKey(Godown_raw_material, on_delete=models.CASCADE, related_name='destination_godowns')
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)



class RawStockTrasferRecords(models.Model):
    master_instance = models.ForeignKey(RawStockTransferMaster, on_delete = models.CASCADE)
    item_shade_transfer = models.ForeignKey(item_color_shade , on_delete= models.CASCADE)
    item_quantity_transfer = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    remarks = models.CharField(max_length = 255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)


class item_purchase_voucher_master(models.Model):
    purchase_number = models.CharField(max_length = 100, unique = True, null = False, blank = False)
    supplier_invoice_number = models.CharField(max_length = 100)
    ledger_type = models.CharField(max_length = 20, default = 'purchase')
    party_name  = models.ForeignKey(Ledger, on_delete = models.PROTECT)
    fright_transport = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    gross_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    grand_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add = True)


class purchase_voucher_items(models.Model):
    item_purchase_master = models.ForeignKey(item_purchase_voucher_master, on_delete = models.CASCADE)
    item_shade = models.ForeignKey(item_color_shade, on_delete = models.PROTECT)
    quantity_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    amount = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    deleted_directly = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)


class shade_godown_items(models.Model):
    purchase_voucher_godown_item = models.ForeignKey(purchase_voucher_items, on_delete = models.CASCADE)
    godown_id = models.ForeignKey(Godown_raw_material, on_delete = models.PROTECT)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    amount = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    deleted_directly = models.BooleanField(default=False)
    

class shade_godown_items_temporary_table(models.Model):
    unique_id = models.UUIDField()
    godown_id = models.ForeignKey(Godown_raw_material, on_delete= models.CASCADE)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    amount = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    

class item_godown_quantity_through_table(models.Model):
    godown_name = models.ForeignKey(Godown_raw_material, on_delete = models.PROTECT, related_name= 'raw_godown_names')
    Item_shade_name = models.ForeignKey(item_color_shade, related_name = 'godown_shades', on_delete = models.PROTECT)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    item_rate = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = [['godown_name','Item_shade_name']]
        # godown and items unique together as
        # if there are already item in a godown if user again enters quantity instead of creating
        # one more entry for the same item in godown u just need to update the quantity of the item in that
        # godown.


    def __str__(self):
        return f'{self.godown_name}-{self.Item_shade_name} - {self.quantity}'
    
            
class product_2_item_through_table(models.Model):
    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, blank=True, null=True)
    PProduct_pk = models.ForeignKey(PProduct_Creation, on_delete=models.PROTECT)
    Item_pk = models.ForeignKey(Item_Creation, on_delete=models.PROTECT)
    row_number = models.IntegerField(null = True, blank=True)   # row no used to download excel in the same order as form using order_by 
    grand_total = models.DecimalField(default = 0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    grand_total_combi = models.DecimalField(default = 0,max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    common_unique = models.BooleanField(default = False)  #True if its common and false if its special
    no_of_rows = models.PositiveIntegerField(default = 1, validators=[MinValueValidator(1)])
    Remark = models.CharField(max_length = 50, blank = True, null=True)


    class Meta:
        unique_together = [['PProduct_pk','Item_pk']]
        
    
class set_prod_item_part_name(models.Model):

    BODY_COMBI = [
        ('body', 'body'),
        ("combi", 'combi')
    ]

    c_user = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, blank=True, null=True)
    producttoitem = models.ForeignKey(product_2_item_through_table, on_delete=models.CASCADE, related_name='product_item_configs')
    part_name = models.CharField(max_length = 100,blank = True, null= True)
    part_dimentions = models.CharField(max_length=100,blank=True, null= True)
    dimention_total = models.DecimalField(default=0, max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, blank=True, null= True)
    part_pieces = models.IntegerField(blank=True, null = True)
    body_combi = models.CharField(max_length=10, choices = BODY_COMBI, blank=True, null = True)


class factory_employee(models.Model):
    factory_emp_name = models.CharField(max_length= 255, unique=True)
    cutting_room_id = models.ForeignKey('cutting_room',null=True, on_delete=models.PROTECT)


class cutting_room(models.Model):
    cutting_room_name = models.CharField(max_length=100, unique=True)


class purchase_order(models.Model):
    STATUS = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]
    purchase_order_number = models.CharField(max_length=100, unique=True, blank=False, null=False)
    product_reference_number = models.ForeignKey(Product, on_delete=models.PROTECT)
    ledger_party_name = models.ForeignKey(Ledger, on_delete= models.PROTECT)
    target_date = models.DateField()
    created_date = models.DateTimeField(auto_now=True)
    modified_created_date = models.DateTimeField(auto_now_add=True)
    number_of_pieces = models.IntegerField(validators=[MinValueValidator(1)])
    balance_number_of_pieces = models.IntegerField(default=0, blank=True, null = True)
    process_status = models.CharField(max_length=10, choices=STATUS, blank=True, null= True)
    temp_godown_select = models.ForeignKey(Godown_raw_material, on_delete=models.PROTECT)
    cutting_total_processed_qty = models.IntegerField(default=0)
    purchase_order_to_product_saved = models.BooleanField(default=False)
    note = models.TextField(blank=True, null = True)

class purchase_order_to_product(models.Model):
    purchase_order_id = models.ForeignKey(purchase_order, related_name = 'p_o_to_products',on_delete=models.CASCADE)
    product_id = models.ForeignKey(PProduct_Creation, on_delete=models.PROTECT)
    order_quantity = models.IntegerField(default=0)
    order_processed_quantity = models.IntegerField(default=0)
    process_quantity = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    

class purchase_order_for_raw_material(models.Model):
    purchase_order_id = models.ForeignKey(purchase_order,related_name='raw_materials', on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=50)
    product_color = models.CharField(max_length = 60, null=False, blank=False)
    material_name = models.CharField(max_length = 60, null=False, blank=False)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    panha = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    units = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    unit_value = models.CharField(max_length=100)
    g_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    g_total_combi = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    combi_consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    total_comsumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    balance_physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    Remark = models.CharField(max_length = 50, null=False, blank=False)
    pcs = models.IntegerField(default = 0)


class purchase_order_raw_material_cutting(models.Model):
    purchase_order_id = models.ForeignKey(purchase_order, related_name ='cutting_pos', on_delete = models.CASCADE)
    raw_material_cutting_id = models.IntegerField(primary_key=True)
    auto_id = models.PositiveIntegerField(unique=True,blank=False, null= False)
    factory_employee_id = models.ForeignKey(factory_employee, on_delete=models.PROTECT, null=True, blank=True)
    processed_qty  = models.IntegerField(default=0)
    balance_qty = models.IntegerField(default=0)
    approved_qty = models.IntegerField(default=0)
    cutting_cancelled = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null = True)

    # to save an auto field which acts as an autoincrement field
    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = purchase_order_raw_material_cutting.objects.order_by('auto_id').last()

            if last_id:
                self.auto_id = last_id.auto_id + 1
            else:
                self.auto_id = 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["auto_id"]



class purchase_order_to_product_cutting(models.Model): 
    purchase_order_cutting_id = models.ForeignKey(purchase_order_raw_material_cutting, on_delete=models.CASCADE)
    product_color = models.CharField(max_length=100)
    product_sku = models.CharField(max_length=100)
    order_quantity = models.IntegerField(default=0)
    process_quantity = models.IntegerField(default=0)
    cutting_quantity = models.IntegerField(default=0)
    approved_pcs = models.IntegerField(default=0)
    balance_pcs = models.IntegerField(default=0)
    approved_pcs_diffrence = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)


class purchase_order_for_raw_material_cutting_items(models.Model):

    STATUS = [
        ('cutting_room', 'cutting_room'),
        ('cutting_room_cancelled','cutting_room_cancelled'),
    ]

    purchase_order_cutting = models.ForeignKey(purchase_order_raw_material_cutting, on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=50)
    product_color = models.CharField(max_length = 100, null=False, blank=False)
    material_name = models.CharField(max_length = 100, null=False, blank=False)
    material_color_shade = models.ForeignKey(item_color_shade, on_delete=models.PROTECT, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    panha = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    units = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    unit_value = models.CharField(max_length=100)
    g_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    combi_consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    total_comsumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    g_total_combi = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    balance_physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    cutting_room_status = models.CharField(max_length=25, choices = STATUS, blank=True, null=True)
    total_comsumption_in_cutting = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)
    Remark = models.CharField(max_length = 50, null=False, blank=False)
    pcs = models.IntegerField(default = 0)

class labour_workout_master(models.Model):
    purchase_order_cutting_master = models.ForeignKey(purchase_order_raw_material_cutting, related_name='labourworkouts',on_delete=models.CASCADE)
    total_approved_pcs = models.IntegerField(default=0)
    total_pending_pcs = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if self._state.adding:
    #         self.challan_no = self.generate_unique_challan_no()
    #     super().save(*args, **kwargs)

    # def generate_unique_challan_no(self):
    #     max_attempts = 1000
    #     attempts = 0
        
    #     while attempts < max_attempts:
    #         challan_no = int(get_random_string(length=9, allowed_chars='0123456789'))
    #         if not labour_workout_master.objects.filter(challan_no=challan_no).exists():
    #             return challan_no
    #         attempts += 1
        
    #     raise ValueError("Unable to generate a unique challan_no after 1000 attempts")

class product_to_item_labour_workout(models.Model):
    labour_workout = models.ForeignKey(labour_workout_master,related_name='labour_workout_items' ,on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=100)
    product_color = models.CharField(max_length=100)
    processed_pcs = models.IntegerField()
    pending_pcs = models.IntegerField()
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)


class labour_workout_childs(models.Model):
    labour_workout_master_instance = models.ForeignKey(labour_workout_master, on_delete=models.PROTECT)
    challan_no = models.CharField(unique=True, null=False, blank=False)
    labour_name = models.ForeignKey(Ledger, on_delete=models.PROTECT, null=False, blank=False)
    total_process_pcs = models.IntegerField(null = True, blank=True)
    total_balance_pcs = models.IntegerField(null = True, blank=True)
    created_date = models.DateTimeField(auto_now = True)
    modified_date = models.DateTimeField(auto_now_add=True)
    labour_workin_pcs = models.IntegerField(default = 0)
    labour_workin_pending_pcs = models.IntegerField()
    note = models.TextField(null=True, blank=True)


class product_to_item_labour_child_workout(models.Model):
    labour_workout = models.ForeignKey(labour_workout_childs, related_name='labour_workout_child_items', on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=100)
    product_color = models.CharField(max_length=100)
    processed_pcs = models.IntegerField()
    pending_pcs = models.IntegerField()
    balance_pcs = models.IntegerField()
    labour_w_in_pending = models.IntegerField()
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)


class labour_workout_cutting_items(models.Model):
    labour_workout_child_instance = models.ForeignKey(labour_workout_childs, on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=50)
    product_color = models.CharField(max_length = 100, null=False, blank=False)
    material_name = models.CharField(max_length = 100, null=False, blank=False)
    material_color_shade = models.CharField(max_length = 255)
    rate = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    panha = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    units = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    unit_value = models.CharField(max_length=100)
    g_total = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    g_total_combi = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    combi_consumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    total_comsumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    balance_physical_stock = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add = True)
    Remark = models.CharField(max_length = 50, null=False, blank=False)
    pcs = models.IntegerField(default = 0)



class labour_work_in_master(models.Model):
    labour_voucher_number = models.ForeignKey(labour_workout_childs ,on_delete=models.PROTECT)
    voucher_number = models.IntegerField(unique=True, null = False, blank = False)
    created_date = models.DateTimeField(auto_now = True)
    description = models.CharField(max_length=100, null=True, blank=True)
    total_return_pcs = models.IntegerField(null=False, blank=False)
    total_balance_pcs = models.IntegerField(null=False, blank=False)
    total_approved_qty = models.IntegerField(default = 0)
    labour_charges = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    other_charges = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT,null=False, blank=False)
    modified_date = models.DateTimeField(auto_now_add=True)



class labour_work_in_product_to_item(models.Model):
    labour_workin_instance = models.ForeignKey(labour_work_in_master, on_delete=models.CASCADE, related_name='l_w_in_products')
    product_sku = models.CharField(max_length=100)
    product_color = models.CharField(max_length=100)
    L_work_out_pcs = models.IntegerField()
    return_pcs = models.IntegerField()
    pending_to_return_pcs = models.IntegerField()
    pending_for_approval =  models.IntegerField()
    approved_qty = models.IntegerField(default = 0)


# reports
class godown_item_report_for_cutting_room(models.Model):
    creation_date = models.DateTimeField(auto_now = True)
    particular = models.CharField(max_length=100)
    voucher_type = models.CharField(max_length=100)
    voucher_number = models.CharField(max_length=100)
    material_color_shade = models.CharField(max_length=255)
    godown_id = models.CharField(max_length=50)
    inward = models.BooleanField() # true for inward and false for outward
    total_comsumption = models.DecimalField(max_digits=10, decimal_places=DECIMAL_PLACE_CONSTANT)
    rate = models.DecimalField(max_digits=10, decimal_places = DECIMAL_PLACE_CONSTANT)