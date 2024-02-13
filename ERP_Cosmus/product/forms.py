from django import forms
from .models import Color, Fabric_Group_Model, Item_Creation, Product, ProductImage, PProduct_Creation, Unit_Name_Create, item_color_shade
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['Image_ID','Image_type', 'Order_by', 'Image']

ProductImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=1)



class ProductForm(forms.ModelForm):

    widgets = {
            'Product_Channel': forms.CheckboxSelectMultiple,
            }
         
    class Meta:
        model = Product
        fields = ['Product_Name', 'Model_Name', 'Product_Status', 'Product_Channel', 
                  'Product_Brand', 'Product_HSNCode', 'Product_GST', 
                  'Product_WarrantyTime', 'Product_MRP', 'Product_SalePrice_CustomerPrice',
                  'Product_BulkPrice', 'Product_Cost_price']

class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['Product_Name','Model_Name', 'Product_Brand', 'Product_Status', 'Product_Channel',
     'color_primary' ,"Product_Compartments", 'Product_Accessory_Compartments' , 'Product_CapacityLtrs',
     "Product_Material" ,'Product_Dimensions_WP_Length' ,'Product_Dimensions_WP_Height',"Product_Dimensions_WP_Width",
     "Product_Dimensions_WP_Weight" ,'Product_QtyPerBox','Product_WarrantyTime',
     'Product_Dimensions_WOP_Length','Product_Dimensions_WOP_Height', "Product_Dimensions_WOP_Width",
     "Product_Dimensions_WOP_Weight",'Product_BulletPoint1','Product_BulletPoint2','Product_BulletPoint3',
     'Product_BulletPoint4', 'Product_BulletPoint5','Product_ShortDescription','Product_LongDescription',
     'Product_EANCode', 'Product_HSNCode','Product_GST', 'Product_UOM', 'Product_MRP',
     'Product_SalePrice_CustomerPrice' ,'Product_WRP', 'Product_CashCounterPrice' ,'Product_Retailer_dealer_Price',
     'Product_Wholesaler_DistributorPrice' , 'Product_IndiaMartPrice','Product_BulkPrice', 'Product_Cost_price',
     'Amazon_Link','Cosmus_link' ,'Youtube_Link','Flipkart_Link']
        
    images = ProductImageFormSet(queryset=ProductImage.objects.none(), prefix='product_images')




class PProductCreateForm(forms.ModelForm):
    Product_Refrence_ID = forms.IntegerField(label='Product_Refrence_ID')
    class Meta:
        model = PProduct_Creation
        fields = ['PProduct_image','PProduct_color','PProduct_SKU', 'Product_Refrence_ID']


    def clean_PProduct_SKU(self):
        sku = self.cleaned_data['PProduct_SKU']

        # Check if SKU already exists in the database
        if PProduct_Creation.objects.filter(PProduct_SKU=sku).exists():
            raise forms.ValidationError('Product SKU already exists in the database')

        return sku


class PProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['Product_Name', 'Model_Name', 'Product_Status', 'Product_Channel', 
                  'Product_Brand','Product_HSNCode', 'Product_GST', 
                  'Product_WarrantyTime', 'Product_MRP', 'Product_SalePrice_CustomerPrice',
                  'Product_BulkPrice', 'Product_Cost_price', 'Product_Refrence_ID']


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color_name']
        



class Itemform(forms.ModelForm):
    shades = forms.CharField(label='shades')
    class Meta:
        model = Item_Creation
        fields = ['item_name','Material_code','Item_Color','shades','Packing',
                 'unit_name_item','Units','Panha', 'Fabric_nonfabric','Fabric_Finishes','Fabric_Group',
                 'GST','HSN_Code','status']
        



class ItemFabricGroup(forms.ModelForm):
    class Meta:
        model = Fabric_Group_Model 
        fields = ['fab_grp_name']



class UnitName(forms.ModelForm):
    class Meta:
        model = Unit_Name_Create
        fields = ['unit_name']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

# Register a user
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', "password1" , "password2"]