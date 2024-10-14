from dataclasses import fields
from pyexpat import model
from django import forms
from django.shortcuts import get_object_or_404

from core.models import Company
from .models import AccountSubGroup, Color, Fabric_Group_Model, FabricFinishes, Item_Creation, Ledger, MainCategory, RawStockTransferMaster, RawStockTrasferRecords,  StockItem ,Product, ProductImage, PProduct_Creation, SubCategory, Unit_Name_Create, cutting_room,  factory_employee, gst, item_color_shade , ProductVideoUrls,ProductImage, item_godown_quantity_through_table,item_purchase_voucher_master, labour_work_in_master, labour_work_in_product_to_item, labour_workout_childs, labour_workout_cutting_items, labour_workout_master, ledgerTypes, opening_shade_godown_quantity, packaging, product_2_item_through_table, product_to_item_labour_child_workout, product_to_item_labour_workout, purchase_order, purchase_order_for_raw_material, purchase_order_for_raw_material_cutting_items, purchase_order_raw_material_cutting, purchase_order_to_product, purchase_order_to_product_cutting, purchase_voucher_items, shade_godown_items, shade_godown_items_temporary_table
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, BaseInlineFormSet 
from django.db import transaction
import logging
from .mixins import CompanyUniqueFieldMixin, UniqueFieldMixin


logger = logging.getLogger('product_forms')

# notes in notes/customuserandcompany.txt
class CompanyBaseForm(forms.ModelForm):

    """
    A base form that handles company assignment based on the user's role.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Pass the request user in the form
        super().__init__(*args, **kwargs)


    def save(self, commit=True):
        instance = super().save(commit=False)

        # For normal users, auto-assign the company based on the user
        if not self.user.is_superuser:
            instance.c_user = self.user 
            instance.company = self.user.company

        # For superusers, the company is assigined in form which is selected from dropdown
        else:
            instance.c_user = self.user
        
        # if commit is performed
        if commit:
            instance.save()

        return instance
    


class PProductCreateForm(forms.ModelForm):
    class Meta:
        model = PProduct_Creation
        fields = ['PProduct_image','PProduct_color','PProduct_SKU','Product_EANCode']


    def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)  # Extract the user from kwargs
            super(PProductCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(PProductCreateForm, self).save(commit=False)

        # Assign the user if necessary
        if self.user:
            instance.c_user = self.user  # Assuming the model has a 'user' field

        if commit:
            instance.save()

        return instance



class PProductCreateFormset(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.c_user = kwargs.pop('c_user', None)  # Pop the c_user from kwargs
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """
        Override this method to pass `c_user` (user) to each form.
        """
        kwargs = super().get_form_kwargs(index)
        kwargs['user'] = self.c_user  # Pass c_user (user) to the form
        return kwargs
        


ProductCreateSkuFormsetUpdate = inlineformset_factory(Product, PProduct_Creation,
                                                form=PProductCreateForm,
                                                formset=PProductCreateFormset,
                                                extra=0, can_delete=False)


ProductCreateSkuFormsetCreate = inlineformset_factory(Product, PProduct_Creation,
                                                form=PProductCreateForm,
                                                formset=PProductCreateFormset,
                                                extra=1, can_delete=False)





class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage  # Assuming a model called ProductImage
        fields = ['Image','Image_type','Order_by']  # Example fields

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract the user from kwargs
        super(ProductImageForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ProductImageForm, self).save(commit=False)

        # Assign the user if necessary
        if self.user:
            instance.c_user = self.user  # Assuming the model has a 'user' field

        if commit:
            instance.save()

        return instance
    
class ProductImageFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.c_user = kwargs.pop('c_user', None)  # Pop the c_user from kwargs
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """
        Override this method to pass `c_user` (user) to each form.
        """
        kwargs = super().get_form_kwargs(index)
        kwargs['user'] = self.c_user  # Pass c_user (user) to the form
        return kwargs



class ProductVideoForm(forms.ModelForm):
    class Meta:
        model = ProductVideoUrls  # Assuming a model called ProductVideoUrls
        fields = ['product_video_url']  # Example fields

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract the user from kwargs
        super(ProductVideoForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ProductVideoForm, self).save(commit=False)

        # Assign the user if necessary
        if self.user:
            instance.c_user = self.user  # Assuming the model has a 'user' field

        if commit:
            instance.save()

        return instance



class ProductVideoFormSet1(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.c_user = kwargs.pop('c_user', None)  # Pop the c_user from kwargs
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """
        Override this method to pass `c_user` (user) to each form.
        """
        kwargs = super().get_form_kwargs(index)
        kwargs['user'] = self.c_user  # Pass c_user (user) to the form
        return kwargs




ProductImagesFormSet = inlineformset_factory(PProduct_Creation,ProductImage,formset = ProductImageFormSet,form=ProductImageForm, extra = 1)
ProductVideoFormSet = inlineformset_factory(PProduct_Creation,ProductVideoUrls,formset = ProductVideoFormSet1, form = ProductVideoForm, extra = 1)



class Product2ItemForm(forms.ModelForm):
    class Meta:
        model = product_2_item_through_table
        fields= ['PProduct_pk','Item_pk','Remark','no_of_rows','grand_total','row_number','grand_total_combi']
        
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
Product2ItemFormset = modelformset_factory(product_2_item_through_table,form = Product2ItemForm, extra=0, can_delete=True)
Product2ItemFormsetExtraForm = modelformset_factory(product_2_item_through_table,form = Product2ItemForm, extra=1, can_delete=True)



class Product2CommonItem(forms.ModelForm):
    class Meta:
        model = product_2_item_through_table
        fields= ['Item_pk','Remark','no_of_rows','row_number','grand_total','grand_total_combi']
    
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
    




Product2CommonItemFormSet = modelformset_factory(product_2_item_through_table, form = Product2CommonItem, extra=0, can_delete=True)

Product2CommonItemFormSetExtraForm = modelformset_factory(product_2_item_through_table, form = Product2CommonItem, extra=1, can_delete=True)





class PProductAddForm(UniqueFieldMixin,forms.ModelForm):

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
                  'Product_BulletPoint4','labour_charges',
                  'Product_BulletPoint5','Product_ShortDescription','Product_LongDescription','Product_Dimensions_WP_Length',
                  'Product_Dimensions_WP_Width','Product_Dimensions_WP_Height','Product_Dimensions_WP_Weight',
                  'Product_Dimensions_WOP_Length',
                  'Product_Dimensions_WOP_Width','Product_Dimensions_WOP_Height','Product_Dimensions_WOP_Weight',
                  'Product_WRP','Product_CashCounterPrice','Product_IndiaMartPrice','Product_Retailer_dealer_Price',
                  'Product_Wholesaler_DistributorPrice','Product_Gender',
                  'Product_QtyPerBox']
        
    def clean_Model_Name(self):
        return self.clean_unique_field('Model_Name',Product)
    

    def clean_Product_Name(self):
        return self.clean_unique_field('Product_Name',Product)
        

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





class ColorForm(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color_name']

    def clean_color_name(self):
        return self.clean_unique_field('color_name', Color)
    
    """
        OR
            def clean_color_name(self):
        data = self.cleaned_data['color_name']
        
        # Exclude current instance from validation logic when updating 
        colors = Color.objects.exclude(id=self.instance.id)

        #further filter the excluded query if color_name 
        if colors.filter(color_name__iexact = data).exists():
                raise ValidationError('Color already created!')

        return data
    """
            


class Itemform(UniqueFieldMixin,forms.ModelForm):
    
    class Meta:
        model = Item_Creation
        fields = ['item_name','Material_code','Item_Color','Item_Packing',
                 'unit_name_item','Units','Panha', 'Fabric_nonfabric','Item_Fabric_Finishes','Fabric_Group',
                 'Item_Creation_GST','HSN_Code','status','item_shade_image']
        
    def clean_item_name(self):
        return self.clean_unique_field('item_name',Item_Creation)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Retrieve the last instance of the Item_Creation model
        last_item = Item_Creation.objects.order_by('pk').last()
        

        # If there's a previous instance, set Material_code to last_item.pk + 1
        if last_item:
            self.fields['Material_code'].initial = last_item.pk + 1

        else:
            # If no previous instance exists, you can set a default initial value
            self.fields['Material_code'].initial = 1

""" 
explaination on rendering data in - notes_forms_form_api.txt
            
"""



ShadeFormSet = inlineformset_factory(Item_Creation, item_color_shade, fields=('item_name_rank', 'item_shade_name', 'item_color_image'), extra=1)
OpeningShadeFormSetupdate = inlineformset_factory(item_color_shade, opening_shade_godown_quantity, fields=('opening_godown_id', 'opening_quantity', 'opening_rate'), extra=1)



class ItemFabricGroup(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = Fabric_Group_Model 
        fields = ['fab_grp_name']

    def clean_fab_grp_name(self):
        return self.clean_unique_field('fab_grp_name',Fabric_Group_Model)

class UnitName(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = Unit_Name_Create
        fields = ['unit_name','unit_value']


    def clean_unit_name(self):
        return self.clean_unique_field('unit_name',Unit_Name_Create)

class account_sub_grp_form(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = AccountSubGroup
        fields = ['acc_grp', 'account_sub_group']

    def clean_account_sub_group(self):
        return self.clean_unique_field('account_sub_group',AccountSubGroup)


class StockItemForm(CompanyBaseForm):
    class Meta:
        model = StockItem
        fields = ['acc_sub_grp','stock_item_name','company'] # Include company for superusers




class ledger_types_form(forms.ModelForm):
    class Meta:
        model = ledgerTypes

        fields = ['type_name']


    def clean_ledger_types_form(self):
        return self.clean_unique_field('type_name',ledgerTypes)

class LedgerForm(forms.ModelForm):
    opening_balance = forms.IntegerField(label='Opening Balance')
    class Meta:
        model = Ledger
        fields = ['name','short_name','vendor_code','under_group','maintain_billwise',
                  'default_credit_period','types','Gst_no','address','state',
                  'country','city','pincode','mobile_no','landline_no','bank_details',
                  'Debit_Credit']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        last_item = Ledger.objects.order_by('id').last()

        if last_item:

            self.fields['vendor_code'].initial = last_item.id + 1
        else:
            self.fields['vendor_code'].initial = 1


class item_purchase_voucher_master_form(forms.ModelForm):
    class Meta:
        model = item_purchase_voucher_master
        fields = [
            'purchase_number','supplier_invoice_number','ledger_type',
            'party_name','fright_transport','gross_total','grand_total'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        last_item = item_purchase_voucher_master.objects.order_by('id').last()

        if last_item:

            self.fields['purchase_number'].initial = last_item.id + 1
        else:
            self.fields['purchase_number'].initial = 1

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


class packaging_form(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = packaging
        fields = ['packing_material']


    def clean_packing_material(self):
        return self.clean_unique_field('packing_material',packaging)



class FabricFinishes_form(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = FabricFinishes
        fields = ['fabric_finish']
        
    def clean_fabric_finish(self):
        return self.clean_unique_field('fabric_finish', FabricFinishes)


class product_main_category_form(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = MainCategory
        fields = ['product_category_name']

    def clean_product_category_name(self):
        return self.clean_unique_field('product_category_name',MainCategory)



class product_sub_category_form(UniqueFieldMixin,forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['product_sub_category_name','product_main_category']

    def clean_product_sub_category_name(self):
        return self.clean_unique_field('product_sub_category_name',SubCategory)


class purchase_order_form(forms.ModelForm):

    class Meta:
        model = purchase_order

        fields = ['purchase_order_number','product_reference_number','ledger_party_name',
                  'target_date','number_of_pieces','temp_godown_select','balance_number_of_pieces']
        



class purchase_order_to_product_form(forms.ModelForm):
    class Meta:
        model = purchase_order_to_product

        fields = ['product_id','order_quantity']

        widgets = {
            'product_id': forms.TextInput(),
        }

# custom formset for validation extended form BaseInlineFormset

class BasePurchaseOrderProductQtyFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        total_order_quantity = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                # Get the order_quantity from the cleaned_data of each form:
                order_quantity = form.cleaned_data.get('order_quantity')
                total_order_quantity += order_quantity

                # set the process qty same as orderqty using form.insatnce
                form.instance.process_quantity = order_quantity
        
        # Access the parent model's number_of_pieces field
        parent_quantity = self.instance.number_of_pieces  

        # Raise a validation error if the total order quantity exceeds the parent quantity
        if total_order_quantity != parent_quantity:
            raise ValidationError(f'The total order quantity ({total_order_quantity}) exceeds the available quantity ({parent_quantity}) it should equal')


        """
        NOTE ON class BasePurchaseOrderProductQtyFormSet(BaseInlineFormSet):

        with 'self.instance.PARENT FIELD NAME'  we can access parent values 
        AND 
        with 
        for form in self.forms:
            form.cleaned_data.get(''MODEL FIELD NAME'', ''DEFAULT VALUE'')
            OR
            child_instance = form.instance  # Get the child model instance
            OR
            child_instance_fields = form.instance.FIELD NAME
        """


purchase_order_product_qty_formset = inlineformset_factory(purchase_order,
                                                            purchase_order_to_product,
                                                              form=purchase_order_to_product_form,
                                                              formset=BasePurchaseOrderProductQtyFormSet, # custom formset for validation
                                                                extra=0, can_delete=True)


# inherited from purchase_order_to_product_form
class purchase_order_raw_to_product_form(purchase_order_to_product_form):
    class Meta(purchase_order_to_product_form.Meta):  # inherited from purchase_order_to_product_form meta class
        
        fields = purchase_order_to_product_form.Meta.fields + ['process_quantity', 'order_processed_quantity']   # inherited from purchase_order_to_product_form fields of meta class



class Basepurchase_order_raw_product_qty_formset(BaseInlineFormSet):
    
    def clean(self):
        super().clean()

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                # Get the order_quantity from the cleaned_data of each form:
                order_quantity = form.cleaned_data.get('order_quantity', 0)
                proc_color_wise_qty = form.cleaned_data.get('process_quantity', 0)
                
                if order_quantity < proc_color_wise_qty:
                    raise ValidationError(f'order quantity ({proc_color_wise_qty}) exceeds the available order quantity ({order_quantity}).')
        
            



purchase_order_raw_product_qty_formset = inlineformset_factory(purchase_order,
                                                                purchase_order_to_product, 
                                                                form=purchase_order_raw_to_product_form, 
                                                                formset = Basepurchase_order_raw_product_qty_formset,
                                                                extra=0)


class purchase_order_raw_product_sheet_form(forms.ModelForm):

    # extra field added in front end not in table which is populated by initial data 
    # product_color = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        
    # )
    #added product_color to table later on

    class Meta:
        model = purchase_order_for_raw_material

        fields = ['product_sku','product_color','material_name','rate','panha',
                  'units','g_total','g_total_combi','consumption','unit_value',
                  'total_comsumption','combi_consumption','physical_stock','balance_physical_stock']



purchase_order_raw_product_qty_cutting_formset = inlineformset_factory(purchase_order, purchase_order_to_product, form=purchase_order_raw_to_product_form, extra=0)



class raw_material_stock_trasfer_master_form(forms.ModelForm):
        class Meta:
            model = RawStockTransferMaster
            fields = ['voucher_no','source_godown','destination_godown']

raw_material_stock_trasfer_items_formset = inlineformset_factory(RawStockTransferMaster,RawStockTrasferRecords,fields=['item_shade_transfer','item_quantity_transfer','remarks'], extra=1, can_delete=True)



class purchase_order_raw_material_cutting_form(forms.ModelForm):
    class Meta:
        model = purchase_order_raw_material_cutting
        fields = ['purchase_order_id','raw_material_cutting_id','factory_employee_id','processed_qty','balance_qty']

        widgets = {
            'purchase_order_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        auto_field_last = purchase_order_raw_material_cutting.objects.order_by('auto_id').last()

        if auto_field_last:
            self.fields['raw_material_cutting_id'].initial = auto_field_last.auto_id + 1
        else:
            self.fields['raw_material_cutting_id'].initial = 1

        



class purchase_order_to_product_cutting_form(forms.ModelForm):

    class Meta:
        model = purchase_order_to_product_cutting

        fields = ['product_color','product_sku','order_quantity','process_quantity','cutting_quantity']



class purchase_order_for_raw_material_cutting_items_form(forms.ModelForm):

    #extra field added in front end 
    purchase_order_pk = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'readonly'}),
        
    )
    class Meta:
        model = purchase_order_for_raw_material_cutting_items

        fields = ['product_sku','product_color','material_name','rate','panha','units','g_total',
                  'consumption','total_comsumption','combi_consumption','physical_stock','balance_physical_stock','unit_value',
                  'material_color_shade','purchase_order_pk','g_total_combi']
        



class Basepurchase_order_for_raw_material_cutting_items_form(BaseInlineFormSet):
    
    def clean(self):
        super().clean()

        # get the data from parent instance
        # po_godown = self.instance.purchase_order_cutting_id.purchase_order_id.temp_godown_select
        
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                try:
                    with transaction.atomic():
                        Purchase_order_pk = form.cleaned_data.get('purchase_order_pk')

                        if not Purchase_order_pk:
                            raise ValidationError("Purchase order primary key is missing.")
                        
                        po_instance = get_object_or_404(purchase_order,id=Purchase_order_pk)
                        po_godown = po_instance.temp_godown_select
                        total_consumption = form.cleaned_data.get('total_comsumption')
                        material_color_shade = form.cleaned_data.get('material_color_shade')
                        
                        if material_color_shade is None and total_consumption != 0:
                            raise ValidationError("please choose from correct shade")
                        
                        elif material_color_shade is not None:
                            if material_color_shade.items.Fabric_nonfabric == 'Fabric':

                                # try:
                                #     item_in_godown = item_godown_quantity_through_table.objects.get(godown_name=po_godown,Item_shade_name=material_color_shade)

                                # except item_godown_quantity_through_table.DoesNotExist:
                                #     raise ValidationError(f'No such item {material_color_shade} in godown {po_godown}.')
                                
                                # item_quantity_in_godown = item_in_godown.quantity

                                # if item_quantity_in_godown >= total_consumption:
                                #     item_in_godown.quantity = item_in_godown.quantity - total_consumption
                                #     item_in_godown.save()

                                # else:
                                #     raise ValidationError(f'Insufficient quantity in godown {po_godown} for material {material_color_shade}. Required: {total_consumption},Available: {item_quantity_in_godown}')


                                try:
                                    item_in_godown = item_godown_quantity_through_table.objects.get(godown_name=po_godown,Item_shade_name = material_color_shade)
                                    item_quantity_in_godown = item_in_godown.quantity

                                except item_godown_quantity_through_table.DoesNotExist:
                                    item_in_godown = item_godown_quantity_through_table(godown_name=po_godown,Item_shade_name = material_color_shade)
                                    item_quantity_in_godown = 0

                                item_in_godown.quantity = item_quantity_in_godown - total_consumption
                                item_in_godown.save()

                                if total_consumption != 0:
                                    form.instance.cutting_room_status = 'cutting_room'
                        

                except purchase_order.DoesNotExist:
                    raise ValidationError(f'Purchase order with ID {Purchase_order_pk} does not exist.')
                
                except item_godown_quantity_through_table.DoesNotExist as e:
                    logger.error(f'Item not found in godown: {e}')
                    form.add_error(None, e)
                    raise

                except ValidationError as e:
                    logger.error(f'Validation error: {e}')
                    form.add_error(None, e)
                    raise

                except Exception as e:
                    logger.error(f'Unexpected error occurred: {e}', exc_info=True)
                    form.add_error(None, e)
                    raise ValidationError(f'An unexpected error occurred: {e}')



purchase_order_cutting_approval_formset = inlineformset_factory(
    purchase_order_raw_material_cutting,purchase_order_to_product_cutting,fields=[
        'product_color','product_sku','cutting_quantity',
        'approved_pcs','balance_pcs','approved_pcs_diffrence'],
          extra=0, can_delete=False)





class labour_workout_child_form(forms.ModelForm):
    total_approved_pcs = forms.IntegerField()
    
    class Meta:
        model = labour_workout_childs
        fields = ['labour_name', 'challan_no','total_approved_pcs',
                  'total_process_pcs','total_balance_pcs']
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        last_id = labour_workout_childs.objects.order_by('id').last()

        if last_id:
            self.fields['challan_no'].initial = last_id.id + 1
        else:
            self.fields['challan_no'].initial = 1






class labour_workout_cutting_items_form(forms.ModelForm):
    fab_non_fab = forms.CharField(max_length=25)
    class Meta:
        model = labour_workout_cutting_items
        fields = ['product_sku','product_color','material_name','material_color_shade','rate'
                  ,'panha','units','g_total','consumption','total_comsumption','combi_consumption','physical_stock','unit_value','g_total_combi'
                  ,'balance_physical_stock' ,'fab_non_fab']
        
    




class labour_workin_master_form(forms.ModelForm):

    labour_name = forms.CharField()
    challan_no = forms.CharField()
    purchase_order_no = forms.CharField()
    refrence_number = forms.IntegerField()
    model_name = forms.CharField()
    total_p_o_qty = forms.IntegerField()
    labour_workout_qty = forms.IntegerField()
    

    class Meta:

        model = labour_work_in_master
        fields = ['voucher_number', 'total_return_pcs', 'labour_charges', 'other_charges', 'amount', 
                   'description','total_balance_pcs']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        last_item = labour_work_in_master.objects.order_by('id').last()

        if last_item:

            self.fields['voucher_number'].initial = last_item.id + 1
        else:
            self.fields['voucher_number'].initial = 1

    
    def clean(self):
        super().clean()

        return_pcs = self.cleaned_data.get('total_return_pcs')
        pending_qty = self.cleaned_data.get('pending_pcs')

        if return_pcs and pending_qty:
            if return_pcs > pending_qty:
                raise ValidationError(f'return pcs{return_pcs} are greater than avaliable pcs{pending_qty}')

            

class labour_work_in_product_to_item_form(forms.ModelForm):

    qty_to_compare = forms.IntegerField()
    cur_bal_plus_return_qty = forms.IntegerField()
    
    class Meta:
        model = labour_work_in_product_to_item
        fields = ['product_sku','product_color','L_work_out_pcs','return_pcs',
                  'pending_to_return_pcs','qty_to_compare','cur_bal_plus_return_qty']

class labour_work_in_product_to_item_approval_form(forms.ModelForm):
    class Meta:
        model = labour_work_in_product_to_item
        fields = ['product_sku','product_color','L_work_out_pcs','return_pcs',
                  'approved_qty','pending_for_approval']
        

labour_work_in_product_to_item_approval_formset = inlineformset_factory(labour_work_in_master,labour_work_in_product_to_item, 
            form = labour_work_in_product_to_item_approval_form, extra = 0, can_delete = False)

class cutting_room_form(CompanyBaseForm):  #UniqueFieldMixin,
    class Meta:
        model = cutting_room
        fields = ['cutting_room_name','company'] # company only for superusers

    # this way we can use a custom mixin or the below commented code 
    # def clean_cutting_room_name(self):
    #     return self.clean_unique_field('cutting_room_name',cutting_room)



class factory_employee_form(CompanyBaseForm):  #UniqueFieldMixin,
    class Meta:
        model = factory_employee
        fields = ['factory_emp_name','cutting_room_id', 'company'] #company only for superusers

    # def clean_factory_emp_name(self):
    #     return self.clean_unique_field('factory_emp_name',factory_employee)
    


















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



