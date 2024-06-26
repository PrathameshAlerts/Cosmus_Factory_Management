from dataclasses import fields
from pyexpat import model
from django import forms
from .models import AccountSubGroup, Color, Fabric_Group_Model, FabricFinishes, Godown_finished_goods, Godown_raw_material, Item_Creation, Ledger, MainCategory, RawStockTransferMaster, RawStockTrasferRecords,  StockItem ,Product, ProductImage, PProduct_Creation, SubCategory, Unit_Name_Create, factory_employee, gst, item_color_shade , ProductVideoUrls,ProductImage,item_purchase_voucher_master, opening_shade_godown_quantity, packaging, product_2_item_through_table, purchase_order, purchase_order_for_raw_material, purchase_order_for_raw_material_cutting_items, purchase_order_raw_material_cutting, purchase_order_to_product, purchase_voucher_items, shade_godown_items, shade_godown_items_temporary_table
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput , DateInput
from django.forms import IntegerField, modelformset_factory, BaseInlineFormSet 



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





class Product2ItemForm(forms.ModelForm):
    class Meta:
        model = product_2_item_through_table
        fields= ['PProduct_pk','Item_pk','Remark','no_of_rows','row_number']
        
    # validate so that the entered value should not be less then the existing value
    def clean_no_of_rows(self):
        new_value = self.cleaned_data.get('no_of_rows')

        if self.instance.pk:
            existing_instance = product_2_item_through_table.objects.get(pk=self.instance.pk)
            existing_value = existing_instance.no_of_rows

            # Compare new value with the existing value
            if new_value < existing_value:
                raise forms.ValidationError(f'The number of rows cannot be less than the current value of {existing_value}.')

        return new_value

# when using modelformset need to add can_delete = True or delete wont be added in form
Product2ItemFormset = modelformset_factory(product_2_item_through_table,form = Product2ItemForm, extra=1, can_delete=True)


class Product2CommonItem(forms.ModelForm):
    class Meta:
        model = product_2_item_through_table
        fields= ['Item_pk','Remark','no_of_rows','row_number']
    
    # validate so that the entered value should not be less then the existing value
    def clean_no_of_rows(self):
        new_value = self.cleaned_data.get('no_of_rows')

        if self.instance.pk:
            existing_instance = product_2_item_through_table.objects.get(pk=self.instance.pk)
            existing_value = existing_instance.no_of_rows

            # Compare new value with the existing value
            if new_value < existing_value:
                raise forms.ValidationError(f'The number of rows cannot be less than the current value of {existing_value}.')

        return new_value


Product2CommonItemFormSet = modelformset_factory(product_2_item_through_table, form = Product2CommonItem, extra=1, can_delete=True)







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




            


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color_name']
        
class Itemform(forms.ModelForm):
    
    class Meta:
        model = Item_Creation
        fields = ['item_name','Material_code','Item_Color','Item_Packing',
                 'unit_name_item','Units','Panha', 'Fabric_nonfabric','Item_Fabric_Finishes','Fabric_Group',
                 'Item_Creation_GST','HSN_Code','status','item_shade_image']
        


ShadeFormSet = inlineformset_factory(Item_Creation, item_color_shade, fields=('item_name_rank', 'item_shade_name', 'item_color_image'), extra=1)
OpeningShadeFormSetupdate = inlineformset_factory(item_color_shade, opening_shade_godown_quantity, fields=('opening_godown_id', 'opening_quantity', 'opening_rate'), extra=1)





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
            'party_name','fright_transport','gross_total','grand_total'
        ]



purchase_voucher_items_formset = inlineformset_factory(item_purchase_voucher_master, purchase_voucher_items, fields=('item_shade', 'quantity_total','rate','amount'), extra=1)
purchase_voucher_items_formset_update = inlineformset_factory(item_purchase_voucher_master, purchase_voucher_items, fields=('item_shade', 'quantity_total','rate','amount'), extra=0)
purchase_voucher_items_godown_formset = inlineformset_factory(purchase_voucher_items,shade_godown_items, fields = ('godown_id','quantity','rate','amount'),extra=0)

purchase_voucher_items_godown_formset_shade_change = inlineformset_factory(purchase_voucher_items,shade_godown_items, fields = ('godown_id','quantity','rate','amount'),extra=1)

class shade_godown_items_temporary_table_form(forms.ModelForm):
    class Meta:
        model = shade_godown_items_temporary_table
        fields = '__all__'

shade_godown_items_temporary_table_formset = modelformset_factory(shade_godown_items_temporary_table, form = shade_godown_items_temporary_table_form, extra=1)

shade_godown_items_temporary_table_formset_update = modelformset_factory(shade_godown_items_temporary_table, form = shade_godown_items_temporary_table_form, extra=0)


class gst_form(forms.ModelForm):
    class Meta:
        model = gst
        fields = ['gst_percentage']


class packaging_form(forms.ModelForm):
    class Meta:
        model = packaging
        fields = ['packing_material']


class FabricFinishes_form(forms.ModelForm):
    class Meta:
        model = FabricFinishes
        fields = ['fabric_finish']


class product_main_category_form(forms.ModelForm):
    class Meta:
        model = MainCategory
        fields = ['product_category_name']



class product_sub_category_form(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['product_sub_category_name','product_main_category']



class purchase_order_form(forms.ModelForm):

    class Meta:
        model = purchase_order

        fields = ['purchase_order_number','product_reference_number','ledger_party_name',
                  'target_date','number_of_pieces']
        


class purchase_order_to_product_form(forms.ModelForm):
    class Meta:
        model = purchase_order_to_product

        fields = ['product_id','order_quantity']

        widgets = {
            'product_id': forms.TextInput(),
        }

purchase_order_product_qty_formset = inlineformset_factory(purchase_order, purchase_order_to_product, form=purchase_order_to_product_form, extra=0, can_delete=True)


# inherited from purchase_order_to_product_form
class purchase_order_raw_to_product_form(purchase_order_to_product_form):
    class Meta(purchase_order_to_product_form.Meta):  # inherited from purchase_order_to_product_form meta class
        
        fields = purchase_order_to_product_form.Meta.fields + ['process_quantity']   # inherited from purchase_order_to_product_form fields of meta class


purchase_order_raw_product_qty_formset = inlineformset_factory(purchase_order, purchase_order_to_product, form=purchase_order_raw_to_product_form, extra=0)


class purchase_order_raw_product_sheet_form(forms.ModelForm):

    # extra field added in front end not in table which is populated by initial data 
    # product_color = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        
    # )
    #added product_color to table later on

    class Meta:
        model = purchase_order_for_raw_material

        fields = ['product_color','material_name','rate','panha','units','g_total','consumption','total_comsumption','physical_stock','balance_physical_stock']



purchase_order_raw_product_qty_cutting_formset = inlineformset_factory(purchase_order, purchase_order_to_product, form=purchase_order_raw_to_product_form, extra=0)



class raw_material_stock_trasfer_master_form(forms.ModelForm):
        class Meta:
            model = RawStockTransferMaster
            fields = ['voucher_no','source_godown','destination_godown']

raw_material_stock_trasfer_items_formset = inlineformset_factory(RawStockTransferMaster,RawStockTrasferRecords,fields=['item_shade_transfer','item_quantity_transfer','remarks'], extra=1, can_delete=True)



class purchase_order_raw_material_cutting_form(forms.ModelForm):
    class Meta:
        model = purchase_order_raw_material_cutting
        fields = ['purchase_order_id','raw_material_cutting_id','factory_employee_id']

        widgets = {
            'purchase_order_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }

class purchase_order_for_raw_material_cutting_items_form(forms.ModelForm):
    class Meta:
        model = purchase_order_for_raw_material_cutting_items

        fields = ['product_color','material_name','rate','panha','units','g_total','consumption','total_comsumption','physical_stock','balance_physical_stock','cutting_quantity']






class factory_employee_form(forms.ModelForm):
    class Meta:
        model = factory_employee
        fields = ['factory_emp_name']























class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())



# Register a user
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', "password1" , "password2"]











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



