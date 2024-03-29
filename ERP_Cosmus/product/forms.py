from django import forms
from .models import AccountSubGroup, Color, Fabric_Group_Model, Godown_finished_goods, Godown_raw_material, Item_Creation, Ledger,StockItem ,Product, ProductImage, PProduct_Creation, Unit_Name_Create, item_color_shade , ProductVideoUrls,ProductImage,item_purchase_voucher_master, purchase_voucher_items, shade_godown_items
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput



class PProductCreateForm(forms.ModelForm):
    Product_Refrence_ID = forms.IntegerField(label='Product_Refrence_ID')
    class Meta:
        model = PProduct_Creation
        fields = ['PProduct_image','PProduct_color','PProduct_SKU', 'Product_Refrence_ID',
                  'Product_EANCode','Product_Rating','Amazon_Link','Flipkart_Link',
                  'Cosmus_link']


        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['Color'].widget.attrs['data-popup'] = True

    def clean_PProduct_SKU(self):
        sku = self.cleaned_data['PProduct_SKU']

        # Check if SKU already exists in the database
        if PProduct_Creation.objects.filter(PProduct_SKU=sku).exists():
            raise forms.ValidationError('Product SKU already exists in the database')

        return sku

ProductImagesFormSet = inlineformset_factory(PProduct_Creation,ProductImage, fields = ['Image','Image_type','Order_by'], extra =1)


ProductVideoFormSet = inlineformset_factory(PProduct_Creation,ProductVideoUrls, fields = ['product_video_url'],extra=1)


class PProductAddForm(forms.ModelForm):

    widgets = {
            'Product_Channel': forms.CheckboxSelectMultiple,
            }
    
    class Meta:
        model = Product
        fields = ['Product_Name', 'Model_Name', 'Product_Status', 'Product_Channel','Product_Brand',
                  'Product_HSNCode', 'Product_GST','Product_WarrantyTime', 'Product_MRP',
                  'Product_SalePrice_CustomerPrice','Product_BulkPrice', 'Product_Cost_price',
                  'Product_ShortName','Product_Refrence_ID',
                  'Product_Compartments','Product_UOM','Product_Accessory_Compartments','Product_CapacityLtrs',
                  'Product_BulletPoint2','Product_BulletPoint1','Product_Material','Product_BulletPoint3',
                  'Product_BulletPoint4',
                  'Product_BulletPoint5','Product_ShortDescription','Product_LongDescription','Product_Dimensions_WP_Length',
                  'Product_Dimensions_WP_Width','Product_Dimensions_WP_Height','Product_Dimensions_WP_Weight',
                  'Product_Dimensions_WOP_Length',
                  'Product_Dimensions_WOP_Width','Product_Dimensions_WOP_Height','Product_Dimensions_WOP_Weight',
                  'Product_WRP','Product_CashCounterPrice','Product_IndiaMartPrice','Product_Retailer_dealer_Price',
                  'Product_Wholesaler_DistributorPrice','Product_Gender',
                  'Product_QtyPerBox']
        


PProductaddFormSet = inlineformset_factory(Product, PProduct_Creation, fields=('PProduct_image', 'PProduct_color', 'PProduct_SKU','Product_EANCode','Product_Rating',
                                                                               'Amazon_Link','Flipkart_Link','Cosmus_link'),extra=0)


# Customize the formset to make PProduct_SKU read-only
class CustomPProductaddFormSet(PProductaddFormSet):

    def __init__(self, *args, **kwargs):
        super(CustomPProductaddFormSet, self).__init__(*args, **kwargs)

        # Loop through the forms in the formset
        for form in self.forms:
            # Set PProduct_SKU field as read-only
            form.fields['PProduct_SKU'].widget.attrs['readonly'] = True



"""
    Initialization: The __init__ method is used to set up initial values, 
    configurations, or any other setup tasks when creating a new instance of the form.

    Customization: It allows you to customize the behavior of the form instance.
    You can customize field attributes, set initial values, define choices dynamically,
    and perform any other necessary setup tasks.

    Access to Data: It provides access to data passed during form initialization,
    such as instance data, form data, or additional keyword arguments.

    Flexibility: By overriding the __init__ method, you can customize the behavior
    of your form according to your specific requirements. This makes your forms more 
    flexible and adaptable to different scenarios.

    Integration with Django Models: When working with Django forms, you often need to
    integrate them with Django models. The __init__ method allows you to handle model instances,
    set initial values based on model data, and perform other tasks related to model forms.

    In the context of Django forms, the __init__ method is often used to customize form fields,
    set initial values, integrate with model instances, and perform other initialization tasks
    to ensure that the form behaves as expected in different scenarios.


"""
        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     instance = kwargs.get('instance')
    #     print('instance=',instance.Product_Name)
    #     if instance:
    #         if instance.Product_Name is None:
    #             self.initial['Product_Name'] = 'test'
    #         if instance.Model_Name is None:
    #             self.initial['Model_Name'] = ' '
    #         if instance.Product_Status is None:
    #             self.initial['Product_Status'] = ' '
    #         if instance.Product_Brand is None:
    #             self.initial['Product_Brand'] = ' '
    #         if instance.Product_WarrantyTime is None:
    #             self.initial['Product_WarrantyTime'] = ' '
    #         if instance.Product_GST is None:
    #             self.initial['Product_GST']
    #     print('instance=',instance.Product_Name)
            



class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color_name']
        


class Itemform(forms.ModelForm):
    
    class Meta:
        model = Item_Creation
        fields = ['item_name','Material_code','Item_Color','Packing',
                 'unit_name_item','Units','Panha', 'Fabric_nonfabric','Fabric_Finishes','Fabric_Group',
                 'Item_Creation_GST','HSN_Code','status','item_shade_image']
        

ShadeFormSet = inlineformset_factory(Item_Creation, item_color_shade, fields=('item_name_rank', 'item_shade_name', 'item_color_image'), extra=1)



class ItemFabricGroup(forms.ModelForm):
    class Meta:
        model = Fabric_Group_Model 
        fields = ['fab_grp_name']



class UnitName(forms.ModelForm):
    class Meta:
        model = Unit_Name_Create
        fields = ['unit_name']


class account_sub_grp_form(forms.ModelForm):
    class Meta:
        model = AccountSubGroup
        fields = ['acc_grp', 'account_sub_group']


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['acc_sub_grp','stock_item_name']




class LedgerForm(forms.ModelForm):
    opening_balance = forms.IntegerField(label='Opening Balance')
    class Meta:
        model = Ledger
        fields = ['name','short_name','vendor_code','under_group','maintain_billwise',
                  'default_credit_period','types','Gst_no','address','state',
                  'country','city','pincode','mobile_no','landline_no','bank_details',
                  'Debit_Credit']

class item_purchase_voucher_master_form(forms.ModelForm):
    class Meta:
        model = item_purchase_voucher_master
        fields = [
            'purchase_number','supplier_invoice_number','ledger_type',
            'party_name','fright_transport','gross_total', 'gst_rate','grand_total'
        ]


purchase_voucher_items_formset = inlineformset_factory(item_purchase_voucher_master, purchase_voucher_items, fields=('item_shade', 'quantity_total','rate','amount'), extra=1)
purchase_voucher_items_godown_formset = inlineformset_factory(purchase_voucher_items,shade_godown_items, fields = ('godown_select','quantity','rate','amount'),extra=1)





class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())



# Register a user
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', "password1" , "password2"]