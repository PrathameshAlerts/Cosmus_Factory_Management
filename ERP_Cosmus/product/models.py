from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator


class CompanyMaster(models.Model):
    company_name =models.CharField(max_length=100) 
    Gst_number = models.CharField(max_length = 15,validators = [MinLengthValidator(15), MaxLengthValidator(15)])



class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)


class MainCategory(models.Model):
    product_category_name = models.CharField(max_length = 250, unique = True)

    def __str__(self):
        return self.product_category_name   


class SubCategory(models.Model):
    product_sub_category_name = models.CharField(max_length = 250)
    product_main_category = models.ForeignKey(MainCategory, on_delete = models.PROTECT, related_name = 'subcategories')

    class Meta:
        unique_together = [['product_sub_category_name','product_main_category']]

    def __str__(self):
        return self.product_sub_category_name 


class Product2SubCategory(models.Model):
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
    color_name = models.CharField( max_length=255, unique= True, null = False, blank = False)

    def __str__(self):
        return self.color_name
    
class gst(models.Model):
    gst_percentage = models.IntegerField(unique=True)
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


    Product_Name = models.CharField(max_length=255, blank = True, null = True, unique=True)
    Model_Name = models.CharField(max_length=255, blank = True,null =True)
    Product_Brand = models.CharField(max_length=200, choices= BRAND_CHOICES , blank = True, null = True)
    Product_Status= models.CharField(max_length=100, choices= PRODUCT_STATUS,  blank = True, null = True)
    Product_Channel= MultiSelectField(max_length=100 , choices = PRODUCT_CHANNEL , blank = True)
    Product_Refrence_ID = models.PositiveIntegerField(unique = True, blank = False,null =True)
    Product_Cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank = True, null = True)
    Product_MRP = models.DecimalField(max_digits=10, decimal_places=2, blank = True, null = True)
    Product_SalePrice_CustomerPrice= models.DecimalField(max_digits=10, decimal_places=2, blank = True, null = True)
    Product_BulkPrice=models.DecimalField( max_digits=10, decimal_places=2, blank = True, null = True)
    Product_WarrantyTime= models.CharField(max_length=15, choices=WARRANTY_TIME, blank = True, null = True)
    Product_HSNCode = models.BigIntegerField(blank = True,null =True)
    Product_GST = models.ForeignKey(gst, blank = True, on_delete = models.PROTECT, null = True)
    Product_ShortName = models.CharField(max_length=200, blank = True,null =True)
    Product_Compartments=  models.CharField(max_length=50, choices= PRODUCT_COMPARTMENTS,  blank = True,null =True)
    Product_UOM = models.CharField(max_length=50, choices =PRODUCT_UCOM ,  blank = True,null =True)
    Product_Accessory_Compartments= models.CharField(max_length=20, choices = PRODUCT_ACCESSORY_COMPARTMENTS, null=True, blank = True)
    Product_CapacityLtrs = models.PositiveIntegerField(blank = True,null =True)
    Product_Material= models.CharField(max_length=100, choices = PRODUCT_MATERIAL, blank = True,null =True)
    Product_BulletPoint1= models.CharField(max_length=255, blank = True,null =True)
    Product_BulletPoint2= models.CharField(max_length=255, blank = True,null =True)
    Product_BulletPoint3= models.CharField(max_length=255,  blank = True,null =True)
    Product_BulletPoint4= models.CharField(max_length=255,  blank = True,null =True)
    Product_BulletPoint5= models.CharField(max_length=255, blank = True,null =True)
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
    Product_WRP = models.DecimalField(max_digits=10, decimal_places=2,  blank = True,null =True)
    Product_CashCounterPrice=models.DecimalField(max_digits=10, decimal_places=2,  blank = True,null =True)
    Product_IndiaMartPrice=models.DecimalField(max_digits=10, decimal_places=2, blank = True,null =True)
    Product_Retailer_dealer_Price=models.DecimalField(max_digits=10, decimal_places=2,  blank = True,null =True)
    Product_Wholesaler_DistributorPrice=models.DecimalField(max_digits=10, decimal_places=2,  blank = True,null =True)
    Product_Create_Date=models.DateField(auto_now=True)
    Product_Gender= models.CharField(max_length=15, choices= PRODUCT_GENDER, blank = True, null = True)
    Product_QtyPerBox = models.IntegerField(blank = True,null =True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)

    def P_GST(self):
        if self.Product_GST is not None:
            return self.Product_GST.gst_percentage
        else:
            return None  # or any default value you prefer


class PProduct_Creation(models.Model):
    Product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='productdetails')  
    PProduct_image = models.ImageField(upload_to = 'pproduct/images',  blank=True)
    PProduct_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='production_primary_color')
    PProduct_SKU = models.BigIntegerField(primary_key = True)
    Product_EANCode = models.CharField(max_length=100, blank = True)
    Product_Rating = models.FloatField( blank = True, null = True)
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

    Product = models.ForeignKey(PProduct_Creation, on_delete = models.CASCADE, related_name='productaplus')
    heading = models.CharField(max_length = 255)
    details = models.TextField()
    orderby = models.IntegerField()
    images = models.ImageField(upload_to = 'pproduct/images',  blank=True)
    dimensions = models.CharField(max_length = 70, choices = DIMENSIONS)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class ProductVideoUrls(models.Model):
    Product = models.ForeignKey(PProduct_Creation, on_delete = models.CASCADE, related_name='productvideourls')
    product_video_url =  models.URLField(max_length = 255, blank = True)
    Image_Uploaded_at = models.DateTimeField(auto_now=True)
    Image_Modified_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class Fabric_Group_Model(models.Model):
    fab_grp_name = models.CharField(max_length=255,unique= True, null = False, blank = False)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class Unit_Name_Create(models.Model):
    unit_name = models.CharField( max_length=255,unique= True, null = False, blank = False)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)



class FabricFinishes(models.Model):
    fabric_finish =  models.CharField(max_length = 100, unique=True)

class packaging(models.Model):
    packing_material = models.CharField(max_length = 100, unique=True)
    

class Item_Creation(models.Model):
    STATUS =  [
        ("Unused","Unused"),
        ("Used","Used"),
        ("Slow Moving","Slow Moving"),
        ("Dead","Dead"),
        ]

    FandNFB = [
        ("Fabric","Fabric"),
        ("Non Fabric","Non Fabric"),
        ]

    #need to add many to many field to vendor 
    item_name = models.CharField(unique = True, null=False, max_length = 255)
    Material_code = models.CharField(max_length = 255)
    Item_Color = models.ForeignKey(Color, on_delete=models.PROTECT, null=False, related_name='ItemColor')
    Item_Packing = models.ForeignKey(packaging, on_delete=models.PROTECT)
    unit_name_item = models.ForeignKey(Unit_Name_Create, on_delete = models.PROTECT, null=False) 
    Units = models.DecimalField(max_digits=10, decimal_places=2)
    Panha = models.DecimalField(max_digits=10, decimal_places=2)
    Fabric_nonfabric = models.CharField(max_length = 255, choices = FandNFB)
    Item_Fabric_Finishes = models.ForeignKey(FabricFinishes, on_delete = models.PROTECT)
    Fabric_Group = models.ForeignKey(Fabric_Group_Model, on_delete= models.PROTECT)
    Item_Creation_GST = models.ForeignKey(gst, on_delete = models.PROTECT)
    HSN_Code = models.CharField(max_length = 100, blank = True)
    status= models.CharField(max_length = 50, choices= STATUS)
    item_shade_image = models.ImageField(upload_to = 'rawmaterial/images', null=True , blank=True)
    created_date = models.DateTimeField(auto_now= True)
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
    items = models.ForeignKey(Item_Creation, on_delete = models.CASCADE, related_name = 'shades')
    item_name_rank = models.PositiveIntegerField(blank = True, null = True)
    item_shade_name =  models.CharField(max_length=100, null = True, blank = True)
    item_color_image = models.ImageField(upload_to ='rawmaterial/images', null=True , blank=True)
    created_date = models.DateTimeField(auto_now = True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


    def __str__(self) -> str:
        return self.item_shade_name


class opening_shade_godown_quantity(models.Model):
    opening_purchase_voucher_godown_item = models.ForeignKey(item_color_shade, on_delete = models.CASCADE)
    opening_godown_id = models.ForeignKey('Godown_raw_material', on_delete = models.PROTECT)
    opening_quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=1)
    opening_rate = models.DecimalField(max_digits=10, decimal_places=1)



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
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)

    def account_sub_group(self):
        return self.acc_sub_grp.account_sub_group
    


class Ledger(models.Model):
    MAINTAIN_BILLWISE = [
        ("Yes", 'Yes'),
        ("No", 'No'),
    ]

    TYPES = [
        ("Trader", 'Trader'),
        ("Manufacture", 'Manufacture'),
    ]

    DEBIT_CREDIT = [
        ("Debit", 'Debit'),
        ("Credit", 'Credit'),
    ]

    name = models.CharField(max_length = 100, blank = True, unique=True)
    short_name = models.CharField(max_length = 100, blank = True)
    vendor_code = models.CharField(max_length = 100, blank = True)
    under_group  = models.ForeignKey(AccountSubGroup, on_delete = models.PROTECT)
    maintain_billwise = models.CharField(choices = MAINTAIN_BILLWISE, max_length = 30, blank = True)
    default_credit_period = models.CharField(max_length = 100, blank = True)
    types = models.CharField(choices = TYPES , max_length = 30, blank = True)
    Gst_no = models.CharField(max_length = 100,validators = [MinLengthValidator(15), MaxLengthValidator(15)])
    address = models.TextField(blank = True) 
    state = models.CharField(max_length = 255, blank = True)
    country = models.CharField(max_length = 255,  blank=True) 
    city = models.CharField(max_length = 255,  blank=True) 
    pincode = models.IntegerField()
    mobile_no = models.BigIntegerField()
    landline_no = models.BigIntegerField()
    bank_details =  models.TextField(blank = True)
    Debit_Credit =  models.CharField( choices = DEBIT_CREDIT ,max_length = 255, blank = True)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


    def account_sub_group_ledger(self):
        return self.under_group.account_sub_group



class account_credit_debit_master_table(models.Model):
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, blank = False, null = False, related_name = 'transaction_entry')
    debit = models.DecimalField(max_digits=12, decimal_places=2, default = 0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default = 0)
    voucher_no = models.IntegerField(null = True, blank= True, unique=True)
    voucher_type = models.CharField(max_length = 100)
    particulars = models.CharField(max_length = 100)
    create_date = models.DateField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)



class Godown_raw_material(models.Model):
    godown_name_raw = models.CharField(max_length = 225, unique= True)

    def __str__(self) -> str:
        return self.godown_name_raw      



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
    Quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=2)


class Godown_finished_goods(models.Model):
    godown_name_finished = models.CharField(max_length = 225, unique= True)


class RawStockTransfer(models.Model):
    voucher_no = models.AutoField(primary_key=True)
    source_godown = models.CharField(max_length = 200)
    destination_godown = models.CharField(max_length = 200)
    item_name_transfer = models.CharField(max_length = 200)
    item_color_transfer = models.CharField(max_length = 200)
    item_shade_transfer = models.CharField(max_length = 200)
    item_quantity_transfer = models.CharField(max_length = 200)
    item_unit_transfer = models.CharField(max_length = 200)
    remarks = models.CharField(max_length = 255)
    date_and_time = models.DateTimeField(auto_now = True)


class item_purchase_voucher_master(models.Model):
    purchase_number = models.CharField(max_length = 100,unique = True, null = False, blank = False)
    supplier_invoice_number = models.CharField(max_length = 100)
    ledger_type = models.CharField(max_length = 20, default = 'purchase')
    party_name  = models.ForeignKey(Ledger, on_delete = models.PROTECT)
    fright_transport = models.DecimalField(max_digits=10, decimal_places=2)
    gross_total = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now= True)
    modified_date_time = models.DateTimeField(auto_now_add= True)


class purchase_voucher_items(models.Model):
    item_purchase_master = models.ForeignKey(item_purchase_voucher_master, on_delete = models.CASCADE)
    item_shade = models.ForeignKey(item_color_shade, on_delete = models.PROTECT)
    quantity_total = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deleted_directly = models.BooleanField(default=False)


class shade_godown_items(models.Model):
    purchase_voucher_godown_item = models.ForeignKey(purchase_voucher_items, on_delete = models.CASCADE)
    godown_id = models.ForeignKey(Godown_raw_material, on_delete = models.PROTECT)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deleted_directly = models.BooleanField(default=False)
    

class shade_godown_items_temporary_table(models.Model):
    unique_id = models.UUIDField()
    godown_id = models.ForeignKey(Godown_raw_material, on_delete= models.CASCADE)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    


class item_godown_quantity_through_table(models.Model):
    godown_name = models.ForeignKey(Godown_raw_material, on_delete = models.PROTECT, related_name= 'raw_godown_names')
    Item_shade_name = models.ForeignKey(item_color_shade, related_name = 'godown_shades', on_delete = models.PROTECT)
    quantity = models.DecimalField(default = 0, max_digits=10, decimal_places=2)
    item_rate = models.DecimalField(default = 0, max_digits=10, decimal_places=2)


    class Meta:
        unique_together = [['godown_name','Item_shade_name']]
        # godown and items unique together as
        # if there are already item in a godown if user again enters quantity instead of creating
        # one more entry for the same item in godown u just need to update the quantity of the item in that
        # godown.


    def __str__(self):
        return f'{self.godown_name}-{self.Item_shade_name}-{self.quantity}'
    
            


class set_prod_item_part_name(models.Model):
    part_name = models.CharField(max_length=100)
    part_dimentions = models.CharField(max_length=100)
    dimention_total = models.CharField(max_length=100)
    part_pieces = models.IntegerField(default=0)
    part_type = models.CharField(max_length=255) #remark
    


class product_2_item_through_table(models.Model):
    PProduct_pk = models.ForeignKey(PProduct_Creation, on_delete=models.CASCADE)
    Item_pk = models.ForeignKey(Item_Creation, on_delete=models.PROTECT)
    set_prod_config = models.ManyToManyField(set_prod_item_part_name)
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    common_unique = models.BooleanField(default=False)  #True if its common and false if its special


    class Meta:
        unique_together = [['PProduct_pk','Item_pk']]
    

