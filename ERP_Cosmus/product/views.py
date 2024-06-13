from io import BytesIO
from sys import exception
from django.contrib.auth.models import User , Group
from django.core.exceptions import ValidationError , ObjectDoesNotExist
import json
from pandas import json_normalize
import requests
from django.contrib.auth.models import auth 
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.utils.timezone import now
import logging
import urllib.parse
from django.contrib import messages
from django.db.models import Sum
from openpyxl.utils import get_column_letter 
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Protection
from django.forms import modelformset_factory
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse, QueryDict
from . models import (AccountGroup, AccountSubGroup, Color, Fabric_Group_Model,
                       FabricFinishes, Godown_finished_goods, Godown_raw_material,
                         Item_Creation, Ledger, MainCategory, PProduct_Creation, Product,
                           Product2SubCategory,  ProductImage, RawStockTransfer, StockItem,
                             SubCategory, Unit_Name_Create, account_credit_debit_master_table,
                               gst, item_color_shade, item_godown_quantity_through_table,
                                 item_purchase_voucher_master, opening_shade_godown_quantity, packaging, product_2_item_through_table, purchase_order, purchase_voucher_items, set_prod_item_part_name, shade_godown_items,
                                   shade_godown_items_temporary_table)

from .forms import(ColorForm, CreateUserForm, CustomPProductaddFormSet,
                    FabricFinishes_form, ItemFabricGroup, Itemform, LedgerForm,
                     LoginForm,OpeningShadeFormSetupdate, PProductAddForm, PProductCreateForm, ShadeFormSet,
                       StockItemForm, UnitName, account_sub_grp_form, PProductaddFormSet,
                        ProductImagesFormSet, ProductVideoFormSet, purchase_order_form,purchase_voucher_items_godown_formset_shade_change,
                         gst_form, item_purchase_voucher_master_form,
                           packaging_form, product_main_category_form, 
                            product_sub_category_form, purchase_voucher_items_formset,
                             purchase_voucher_items_godown_formset, purchase_voucher_items_formset_update,
                                shade_godown_items_temporary_table_formset,shade_godown_items_temporary_table_formset_update,
                                Product2ItemFormset,Product2CommonItemFormSet)


logger = logging.getLogger('product_views')


"""
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
"""

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


#____________________________Production-Product-View-Start__________________________________

def dashboard(request):
    return render(request,'misc/dashboard.html')


#NOTE : in this form one product can be in only one main-category and multiple sub-categories - CURRENTLY USING THIS LOGIC
def edit_production_product(request,pk):

    gsts = gst.objects.all()
    pproduct = get_object_or_404(Product, Product_Refrence_ID=pk)
    
    #get all the product skus from reverse related model of the ref id 
    product_skus = pproduct.productdetails.all()
    

    products_sku_counts = PProduct_Creation.objects.filter(Product__Product_Refrence_ID=pk).count()

    #filter all product2cat instances 
    prod2cat_instance = Product2SubCategory.objects.filter(Product_id= pproduct.id)
    prod_main_cat_name = ''
    prod_main_cat_id = ''
    prod_sub_cat_dict = {}
    prod_sub_cat_dict_all = {}

    #product instances exists
    if prod2cat_instance.exists():
        prodmaincat = prod2cat_instance.first()
        #get the product maincat name and id 
        prod_main_cat_name = prodmaincat.SubCategory_id.product_main_category.product_category_name
        prod_main_cat_id = prodmaincat.SubCategory_id.product_main_category.id


        # create a dict of subcategories of the saved subcategory for the main category
        for subcat in prod2cat_instance:
            prod_sub_cat_dict[subcat.SubCategory_id.id] = subcat.SubCategory_id.product_sub_category_name


        # create a dict of all subcats of the products main category
        sub_categories = SubCategory.objects.filter(product_main_category = prod_main_cat_id)
        for sub_cat_all in sub_categories:
            prod_sub_cat_dict_all[sub_cat_all.id] = sub_cat_all.product_sub_category_name


    colors = Color.objects.all()
    main_categories = MainCategory.objects.all()

    form = PProductAddForm(instance=pproduct)
    formset = CustomPProductaddFormSet(instance=pproduct)

    if request.method == 'POST':
        product_ref_id = pk
        
        try:
            excel_file = request.FILES.get('excel_file')

            if excel_file:
                file_name = excel_file.name
                product_ref_id_file = file_name.split('_')[-1].split('.')[0]
                
                if not excel_file.name.endswith('.xlsx'):
                    messages.error(request, 'Invalid file format. Please upload a valid Excel file.')
                    logger.error('Invalid file format. Please upload a valid Excel file.')
                    return redirect('pproductlist')
                
                if int(product_ref_id_file) == product_ref_id:
                    with transaction.atomic():
                        wb = load_workbook(excel_file, data_only=True)
                        ws1 = wb['product_special_configs']
                        ws2 = wb['product_common_configs']

                        # ws1
                        grand_total = 0
                        
                        for row in ws1.iter_rows(min_row=2,min_col=1):
                            id = row[0].value
                            item_name = row[1].value
                            product_sku = row[2].value
                            

                            if id is not None:
                                if product_sku is not None and item_name is not None:
                                    part_name = row[3].value
                                    part_dimention = row[4].value
                                    dimention_total = row[5].value
                                    part_pieces = row[6].value
                                    grand_total = grand_total + float(dimention_total)  # calucate grand_total by adding all dimention_totals

                                    if part_name is not None and part_dimention is not None:   # to check if part name and part dimention is there not not then delete the row and minus the no_of rows in parent instance
                                        p2i_config_instance = set_prod_item_part_name.objects.get(id=id)

                                        p2i_config_instance.producttoitem.grand_total = grand_total   # assign grand_total value to grand_total of parent model                 
                                        p2i_config_instance.part_name = part_name
                                        p2i_config_instance.part_dimentions = part_dimention
                                        p2i_config_instance.dimention_total = dimention_total
                                        p2i_config_instance.part_pieces = part_pieces
                                        p2i_config_instance.save()   # save model
                                        p2i_config_instance.producttoitem.save()  # save the parent model
                                    else:
                                        p2i_config_instance = set_prod_item_part_name.objects.get(id=id)  # get the id to delete
                                        p2i_config_instance.producttoitem.no_of_rows = p2i_config_instance.producttoitem.no_of_rows - 1   # minus the no_of_rows in parent model 
                                        p2i_config_instance.delete()
                                        p2i_config_instance.producttoitem.save()

                            else:
                                grand_total = 0

                        # ws2        
                        for product_c in PProduct_Creation.objects.filter(Product__Product_Refrence_ID = pk): #loop through all the products in the sku 
                            product_sku = product_c.PProduct_SKU
                            
                            row_no = 0  # row_no to co relate the record in filtered queryset with the row in the excel to CRUD the data as there are multiple instances of configs belonging to the same itemname and product
                            grand_total = 0
                            
                            for row in ws2.iter_rows(min_row=2,min_col=1):  # for every loop through each row in the sheet
                                
                                id = row[0].value
                                item_name = row[1].value
                                part_name = row[2].value
                                part_dimention = row[3].value
                                dimention_total = row[4].value
                                part_pieces = row[5].value
                                
                                if id is not None and item_name is not None:  # check if that row has an id and item name to remove blank rows 

                                    grand_total = grand_total + float(dimention_total)   # grand total addition for all row 
                                    
                                    # get the p2i instance for the product with the item in row 
                                    p2i_instances = product_2_item_through_table.objects.get(PProduct_pk = product_sku, Item_pk__item_name = item_name, common_unique = True)
                                    
                                    # filter out the  all the configs belonging to that p2I instance and then the config based on row_no which corelates
                                    # with the rows in excel to know which config instance to crud
                                    p2i_instances_configs = set_prod_item_part_name.objects.filter(producttoitem=p2i_instances).order_by('id')[row_no]

                                    if part_name is not None:  # check if part name it there if its not then delete that instance
                                        p2i_instances_configs.part_name = part_name
                                        p2i_instances_configs.part_dimentions = part_dimention
                                        p2i_instances_configs.part_pieces = part_pieces
                                        p2i_instances_configs.dimention_total = dimention_total
                                        p2i_instances_configs.producttoitem.grand_total = grand_total # assign grand_total value to grand_total of parent model

                                        p2i_instances_configs.save()
                                        p2i_instances_configs.producttoitem.save() # save the parent model
                                        row_no = row_no + 1  # increase the row after save

                                    else:
                                        row_no = row_no + 1 # increase the row after save
                                        p2i_instances_configs.producttoitem.no_of_rows = p2i_instances_configs.producttoitem.no_of_rows - 1
                                        p2i_instances_configs.delete()
                                        p2i_instances_configs.producttoitem.save()

                                else:
                                    row_no = 0
                                    grand_total = 0

                else:
                    messages.error(request, 'File with invalid Product Refrence Id uploaded')
                    logger.error("File with invalid Product Refrence Id uploaded")
                    return redirect('pproductlist')
            

        except Exception as e:
            logger.error(f"An error occured - {str(e)} - Product-Name - {pproduct}")
            messages.error(request, f'Error uploading Excel file: {str(e)}')
            return redirect('pproductlist')
        

        form = PProductAddForm(request.POST, request.FILES, instance = pproduct) 
        formset = CustomPProductaddFormSet(request.POST, request.FILES , instance=pproduct)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save(commit=False)
                    formset.save()
            
                    #p_id has the id of the product
                    p_id = form.instance
        
                    #get the ids of subcats selected from the frontend 
                    sub_category_ids = request.POST.getlist('Product_Sub_catagory')
            
                    #filter only all the subcats from table sent from the frontend with respect to pid
                    sub_cat_front_listcomp = [Product2SubCategory.objects.filter(Product_id=p_id,SubCategory_id=sub_cat_id).first() for sub_cat_id in sub_category_ids]
            
                    #filter all the subcats from table of the product
                    sub_cat_backend = [x for x in Product2SubCategory.objects.filter(Product_id=p_id)]

                    #delete the subcats from DB if subcat in the db is not sent from the frontend
                    objects_to_delete = [obj for obj in sub_cat_backend if obj not in sub_cat_front_listcomp]
            
                    for obj in objects_to_delete:
                        obj.delete()


                    #loop through the sub cats sent from the front end and get or create new subcats for the product
                    for sub_cat_id in sub_category_ids:
                        sub_cat = SubCategory.objects.get(id = sub_cat_id)
                        p2c, created = Product2SubCategory.objects.get_or_create(Product_id=p_id, SubCategory_id=sub_cat)

                    # form.Number_of_items = Number_of_items
                    form.save()
                    logger.info(f"product-saved product")
                    logger.info(f"product-formset-saved product")
                    return redirect('pproductlist')

            except exception as e:
                logger.error(f"An exception occured in Product - {e} - Product-name - {pproduct}")
                messages.error(request, f'An exception occured - {e}')
        
        else:
            logger.error(f"Productform not valid - {form.errors} - Product-name - {pproduct}")
            logger.error(f"Product formsets not valid- {formset.errors} - Product-name - {pproduct}")

            return render(request, 'product/edit_production_product.html', {'gsts':gsts,
                                                                            'form':form,
                                                                            'product_skus':product_skus,
                                                                            'formset':formset,
                                                                            'colors':colors,
                                                                            'products_sku_counts':products_sku_counts,
                                                                            'main_categories':main_categories,
                                                                            'prod_main_cat_name':prod_main_cat_name,
                                                                            'prod_main_cat_id':prod_main_cat_id,
                                                                            'prod_sub_cat_dict':prod_sub_cat_dict,
                                                                            'prod_sub_cat_dict_all':prod_sub_cat_dict_all})


    return render(request, 'product/edit_production_product.html',{'gsts':gsts,
                                                                   'form': form,
                                                                   'product_skus':product_skus,
                                                                   'formset':formset,
                                                                   'colors':colors,
                                                                   'products_sku_counts':products_sku_counts,
                                                                   'main_categories':main_categories,
                                                                   'prod_main_cat_name':prod_main_cat_name,
                                                                    'prod_main_cat_id':prod_main_cat_id,
                                                                    'prod_sub_cat_dict':prod_sub_cat_dict,
                                                                    'prod_sub_cat_dict_all':prod_sub_cat_dict_all})


#NOTE: this ajax function belongs to product-edit form
def product2subcategoryproductajax(request):
    selected_main_cat = request.GET.get('p_main_cat')
    sub_cats = SubCategory.objects.filter(product_main_category = selected_main_cat)
    
    sub_cat_dict = {}

    for sub_cat in sub_cats:
        sub_cat_dict[sub_cat.id] = sub_cat.product_sub_category_name 


    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'sub_cat_dict':sub_cat_dict})




def product_color_sku(request,ref_id = None):
    color = Color.objects.all()

    try:
        if request.method == 'POST':
            product_ref_id = request.POST.get('Product_Refrence_ID')
            request_dict = request.POST
            count = 0

            for x in request_dict.keys():
                if x[0:12] == 'PProduct_SKU':
                    count = count + 1

            with transaction.atomic():
                all_sets_valid = False

                try:
                    for i in range(1, count): 
                        # Build field names dynamically 
                        image_field_name = f'PProduct_image_{i}'
                        color_field_name = f'PProduct_color_{i}'
                        sku_field_name = f'PProduct_SKU_{i}'
                        Ean_field_name = f'Product_EANCode_{i}'


                        # Create a dictionary with the dynamic field names
                        data = {
                            'PProduct_color': request.POST.get(color_field_name),
                            'PProduct_SKU': request.POST.get(sku_field_name),
                            'Product_EANCode': request.POST.get(Ean_field_name),
                            'Product_Refrence_ID': product_ref_id
                        }
                        files = {
                            'PProduct_image': request.FILES.get(image_field_name)
                        }
                
                        current_form = PProductCreateForm(data, files)

                        if current_form.is_valid():
                            pproduct = current_form.save(commit=False)
                            # Create a new Product instance or get an existing one based on Product_Refrence_ID
                            # product will be the object retrieved from the db and then created ,created will be a boolean field
                            product, created = Product.objects.get_or_create(Product_Refrence_ID=product_ref_id)
                            #product = Product.objects.create(Product_Refrence_ID=product_ref_id)
                    
                            # Associate the PProduct instance with the Product
                            pproduct.Product = product

                            #The variable pproduct holds the unsaved instance of the PProduct_Creation model. 
                            #This instance is populated with the data from the form, and you can use it to perform 
                            #any additional logic or modifications before finally saving it to the database.
                            pproduct.save()
                            all_sets_valid = True

                        else:
                            all_sets_valid = False
                            #explicitly set transaction to rollback on errors
                            transaction.set_rollback(True)
                            break

                except Exception as e:
                    print('Exception occured:', str(e))
                    messages.error(request, f'Exception occured - {e}')


            if all_sets_valid:
                messages.success(request, f'Products for Refrence ID {product_ref_id} created')
                # reverse is used to generate a url with both the arguments, which then redirect can use to redirect
                return redirect(reverse('edit_production_product', args=[product_ref_id]))
            
            else:

                #Return a response with errors for invalid sets of fields
                return render(request, 'product/product_color_sku.html', {'form':current_form,'color': color})
    except Exception as e:
        print('Exception occured', str(e))
        messages.error(request,'Add a product first for Reference ID')
        
    
    form = PProductCreateForm()
    return render(request, 'product/product_color_sku.html', {'form': form, 'color': color,'ref_id': ref_id})




def pproduct_list(request):
    
    queryset = Product.objects.all().order_by('Product_Name').select_related('Product_GST').prefetch_related('productdetails','productdetails__PProduct_color')
    product_search = request.GET.get('product_search')
  
    if product_search != '' and product_search is not None:
        queryset = Product.objects.filter(Q(Product_Name__icontains=product_search)|
                                            Q(Model_Name__icontains=product_search)|
                                            Q(Product_Refrence_ID__icontains=product_search)|
                                            Q(productdetails__PProduct_SKU__icontains=product_search)).distinct()
   
    context = {'products': queryset}

    return render(request,'product/pproduct_list.html',context=context)


def pproduct_delete(request, pk):
    try:
        product = get_object_or_404(Product,Product_Refrence_ID=pk)
        product.delete()
        messages.success(request,f'Product {product.Product_Name} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {product.Product_Name} because it is referenced by other objects.')
    return redirect('pproductlist')


# used formsets to add related objects on a diffrent page
def add_product_images(request, pk):
    product = PProduct_Creation.objects.get(pk=pk)   #get the instance of the product
    formset = ProductImagesFormSet(instance=product)  # pass the instance to the formset
    
    if request.method == 'POST':
        formset = ProductImagesFormSet(request.POST, request.FILES, instance=product)
        if formset.is_valid():
            formset.save()
            messages.success(request,'Product images sucessfully added.')
            # return redirect(reverse('edit_production_product', args=[product.Product.Product_Refrence_ID]))

            # JavaScript to close the popup window
            close_window_script = """
            <script>
            window.opener.location.reload(true);  // Reload parent window if needed
            window.close();  // Close current window
            </script>
            """

            return HttpResponse(close_window_script)
        else:
            return render(request, 'product/add_product_images.html', {'formset': formset, 'product': product})

    return render(request, 'product/add_product_images.html', {'formset': formset, 'product': product})


def add_product_video_url(request,pk):
    product = PProduct_Creation.objects.get(pk=pk)   #get the instance of the product
    formset = ProductVideoFormSet(instance= product)  # pass the instance to the formset
    if request.method == 'POST':
        formset = ProductVideoFormSet(request.POST, instance=product)
        
        if formset.is_valid():
            formset.save()
            messages.success(request,'Product url sucessfully added.')
            # return redirect(reverse('edit_production_product', args=[product.Product.Product_Refrence_ID]))
            close_window_script = """
            <script>
            window.opener.location.reload(true);  // Reload parent window if needed
            window.close();  // Close current window
            </script>
            """
            return HttpResponse(close_window_script)

    else:
            return render(request, 'product/add_product_videourl.html', {'formset': formset, 'product': product})

    return render(request, 'product/add_product_videourl.html', {'formset': formset, 'product': product})


def definemaincategoryproduct(request,pk=None):

    if pk:
        instance = MainCategory.objects.get(pk=pk)
        title = 'Update'
        message = 'updated'
    else:
        instance = None
        title = 'Create'
        message = 'created'

    main_cats = MainCategory.objects.all()
    form = product_main_category_form(instance=instance)
    if request.method == 'POST':
        form = product_main_category_form(request.POST, instance= instance)
        if form.is_valid():
            form.save()
            if message == 'created':
                messages.success(request,'Main Category created sucessfully')
            if message == 'updated':
                messages.success(request,'Main Category updated sucessfully')
            return redirect('define-main-category-product')
        
    return render(request,'product/definemaincategoryproduct.html',{'form':form,'main_cats':main_cats,'title':title})


def definemaincategoryproductdelete(request,pk):
    try:
        instance = MainCategory.objects.get(pk=pk)
        instance.delete()
        messages.success(request,'Main Category Deleted Successfully.')
    except Exception as e :
        messages.error(request,f'{e}')
    return redirect('define-main-category-product')



def definesubcategoryproduct(request, pk=None):
    if pk:
        instance = SubCategory.objects.get(pk=pk)
        title = 'Update'
        message = 'updated'
    else:
        instance = None
        title = 'Create'
        message = 'created'

    main_categories = MainCategory.objects.all()
    sub_category = SubCategory.objects.all()
    
    
    form = product_sub_category_form(instance = instance)
    if request.method == 'POST':
        try:
            form = product_sub_category_form(request.POST,instance = instance)
            if form.is_valid():
                form.save()
                if message == 'created':
                    messages.success(request,'Sub-Category created sucessfully')
                if message == 'updated':
                    messages.success(request,'Sub-Category updated sucessfully')
            
                return redirect('define-sub-category-product')
        
        except Exception as e:
            messages.error(request,f'An Exception occoured - {e}')

    return render(request,'product/definesubcategoryproduct.html',{'main_categories':main_categories, 'sub_category':sub_category,'form':form,'title':title})


def definesubcategoryproductdelete(request, pk):
    try:
        instance = SubCategory.objects.get(pk=pk)
        instance.delete()
        messages.success(request,'Sub Category Deleted Successfully.')
    except Exception as e:
        messages.error(request,f'An Exception occoured - {e}')    
    return redirect('define-sub-category-product')


#NOTE: in this form one product can be in multiple main-category and multiple sub-categories - CURRENTLY NOT USING THIS LOGIC
def product2subcategory(request):
    products = Product.objects.all()
    sub_category = SubCategory.objects.all()
    main_categories = MainCategory.objects.all()
    
    print(request.POST)
    if request.method == 'POST':

        try:
            #get the product id  from POST request
            product_id_get = request.POST.get('product_name')
            
            # Get the list of sub_category_name values 
            sub_category_ids = request.POST.getlist('sub_category_name')
            
            # get the product instance from the id of post request
            p_id = get_object_or_404(Product, id = product_id_get)

            # filter p2c table with the selected product instance 
            existing_instances =  Product2SubCategory.objects.filter(Product_id=p_id)

            updated_instances_front = []
            
            # loop in the sub_cat selected in the frontend 
            for sub_cat_id in sub_category_ids:
                #get the instance of of the id from subcat table
                s_c_id =  get_object_or_404(SubCategory, id = sub_cat_id)
                #filter the p2c table with the p_id instance and sub cat instance and append to the list 
                p_2_c_instance = Product2SubCategory.objects.filter(Product_id=p_id, SubCategory_id=s_c_id).first() 
                updated_instances_front.append(p_2_c_instance)

            
            # get the pk of all the instances from the POST request
            updated_instance_pk = set(obj.pk for obj in updated_instances_front if obj is not None)
            # loop through instance in the table if check if pk of  instance in table is not in updated instance
            instances_to_delete = [obj for obj in existing_instances if obj.pk not in updated_instance_pk]
            
            # delete the instances_to_delete which obj which are in DB but not sent from POST 
            for obj in instances_to_delete:
                obj.delete()

            # the ids which were not sent from POST but are in DB are deleted  above.
                
            # ex:[11,12,13,18] sent from POST, [11,12,13,14] in DB #14 is deleted and the 
            # remaining are updated or created like: 18 is created as its extra in POST, 14 is deleted from DB and 11,12,13 are updated or created.  
            for sub_cat_id in sub_category_ids:

                # now for saving sub_cat_id has the ids from POST to get saved or updated in DB 
                s_c_id =  get_object_or_404(SubCategory, id = sub_cat_id)

                p2c, created = Product2SubCategory.objects.get_or_create(Product_id=p_id, SubCategory_id=s_c_id)
            messages.success(request,f'Product sucessfully added to {s_c_id.product_sub_category_name}')
        
        except IntegrityError:
            messages.error(request, 'Product already present in Subcategory')

        except Exception as e:
            messages.error(request,f'An Exception occoured - {e}')

    return render(request,'product/product2subcategory.html',{'main_categories':main_categories,'products':products,'sub_category':sub_category})


#NOTE: this ajax function belongs to product2category function
def product2subcategoryajax(request):

    productid = request.GET.get('selected_product_id')
    categoryforselectedproduct = Product2SubCategory.objects.filter(Product_id = productid)
    print(productid)

    dict_result = {}
    print(categoryforselectedproduct)
    for obj in categoryforselectedproduct:
        dict_result[obj.SubCategory_id.id] = obj.SubCategory_id.product_sub_category_name
    
    print(dict_result)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'dict_result':dict_result})
    



#____________________________Product-View-End__________________________________

#_____________________Item-Views-start_______________________

def item_create(request):
    title = 'Item Create'
    gsts = gst.objects.all()
    fab_grp = Fabric_Group_Model.objects.all()
    unit_name = Unit_Name_Create.objects.all()
    packaging_material_all = packaging.objects.all()
    fab_finishes = FabricFinishes.objects.all()
    items_to_clone = Item_Creation.objects.all()
    colors = Color.objects.all()

    
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES)


        if form.is_valid():
            form_instance = form.save()


            logger.info("Item Successfully Created")
            messages.success(request,'Item has been created')
            return redirect(reverse('item-edit', args=[form_instance.id]))
    
        else:
            print(form.errors)
            logger.error(f"item form not valid{form.errors}")
            messages.error(request,'Error with item creation')
            
            return render(request,'product/item_create_update.html', {'gsts':gsts,
                                                                      'fab_grp':fab_grp,
                                                                      'unit_name':unit_name,
                                                                      'colors':colors,
                                                                      'packaging_material_all':packaging_material_all,
                                                                      'fab_finishes':fab_finishes,
                                                                      'title':title,'form':form,'items_to_clone':items_to_clone})
    
    form = Itemform()
    return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
                                                                 'packaging_material_all':packaging_material_all,
                                                                    'fab_finishes':fab_finishes,
                                                                 'form':form,'items_to_clone':items_to_clone})

# in request.get data is sent to server via url and it can be accessed using the name variable 
# which has ?namevaraible = data data from the querystring

# in request.POST u can access data sent to server with name varaible which has data from the
# name= as a key and value=  which has the value from the form
    

def item_clone_ajax(request):
    selected_item_name_value = int(request.GET.get('itemValue'))
    
    if selected_item_name_value:
        selected_item = get_object_or_404(Item_Creation, pk=selected_item_name_value)

        response_data = {'fabric_group':{'fab_g_key':selected_item.Fabric_Group.id,'fab_g_value':selected_item.Fabric_Group.fab_grp_name},
                         'color':{'color_key':selected_item.Item_Color.id,'color_value':selected_item.Item_Color.color_name}, 
                         'material_code':selected_item.Material_code,'packing':{'packing_key':selected_item.Item_Packing.id ,'packing_value':selected_item.Item_Packing.packing_material},
                        'unit_name':{'unit_name_key':selected_item.unit_name_item.id,'unit_name_value':selected_item.unit_name_item.unit_name},
                        'panha':selected_item.Panha,'fab_non_fab':selected_item.Fabric_nonfabric,
                        'fab_finishes':{'fab_finishes_key':selected_item.Item_Fabric_Finishes.id,'fab_finishes_value':selected_item.Item_Fabric_Finishes.fabric_finish},
                        'gst':{'gst_key':selected_item.Item_Creation_GST.id,'gst_value':selected_item.Item_Creation_GST.gst_percentage},
                        'hsn_code':selected_item.HSN_Code,'status':selected_item.status}
    
    return JsonResponse({'response_data':response_data})


def item_list(request):
    g_search = request.GET.get('item_search')
    #select related for loading forward FK relationships and prefetch related for reverse relationship  
    #annotate to make a temp column in item_creation for the sum of all item and its related shades in all godowns 
    queryset = Item_Creation.objects.all().annotate(total_quantity=Sum('shades__godown_shades__quantity')).order_by('item_name').select_related('Item_Color','unit_name_item',
                                                    'Fabric_Group','Item_Creation_GST','Item_Fabric_Finishes',
                                                    'Item_Packing').prefetch_related('shades',
                                                    'shades__godown_shades')


# cannot use icontains on foreignkey fields even if it has data in the fields
    if g_search != '' and  g_search is not None:
        queryset = Item_Creation.objects.filter(Q(item_name__icontains=g_search)|
                                                Q(Item_Color__color_name__icontains=g_search)|
                                                Q(Fabric_Group__fab_grp_name__icontains=g_search))
        

    sort_name = request.GET.get('sort_name')


    if sort_name == "item_name_sort_asc" :
        queryset = Item_Creation.objects.order_by('item_name')
    

    elif sort_name == "item_name_sort_dsc" :
        queryset = Item_Creation.objects.order_by('-item_name')


    elif sort_name == "fabgrp_sort_asc" :
        queryset = Item_Creation.objects.order_by('Fabric_Group__fab_grp_name')


    elif sort_name == "fabgrp_sort_dsc" :
        queryset = Item_Creation.objects.order_by('-Fabric_Group__fab_grp_name')

    elif sort_name == "item_color_sort_dsc" :
        queryset = Item_Creation.objects.order_by('Item_Color__color_name')
    
    elif sort_name == "item_color_sort_dsc" :
        queryset = Item_Creation.objects.order_by('-Item_Color__color_name')

    any_desc = request.GET.get('any_desc')
    exact_desc = request.GET.get('exact_desc')

    if any_desc:
        if any_desc != '' and any_desc is not None:
            queryset = Item_Creation.objects.filter(item_name__icontains=any_desc)
        
    if exact_desc:
        if exact_desc != '' and exact_desc is not None:
            queryset = Item_Creation.objects.filter(item_name__exact=exact_desc)

    return render(request,'product/list_item.html', {"items":queryset})
    


def item_edit(request,pk): 
    
    title = 'Item update'
    gsts = gst.objects.all()
    fab_grp = Fabric_Group_Model.objects.all()
    unit_name = Unit_Name_Create.objects.all()
    colors = Color.objects.all()
    packaging_material_all = packaging.objects.all()
    fab_finishes = FabricFinishes.objects.all()
    item_pk = get_object_or_404(Item_Creation,pk = pk)

    form = Itemform(instance = item_pk)
    formset = ShadeFormSet(instance= item_pk)

    print(request.POST)
    # when in item_edit the item is edited u can also edit or add shades to it which also gets updated or added
    # as item_edit instance is also provided while updating or adding with formsets to the shades module
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES , instance=item_pk)
        formset = ShadeFormSet(request.POST , request.FILES, instance=item_pk)

        if form.is_valid() and formset.is_valid():
            form.save()

            for form in formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            for form in formset:
                if form.is_valid():
                    if form.instance.pk:
                        form.save()
                    else:  
                        if not form.cleaned_data.get('DELETE'): # to check if form dosen't have delete in it as it will get saved again if deleted from above code 
                            shade_form_instance = form.save(commit=False)
                            shade_form_instance.save()

                            form_prefix_number = form.prefix[-1] # gives the prefix number of the current iteration of the form
                            opening_godown_quantity = request.POST.get(f'shades-{form_prefix_number}-openingValue')

                            if opening_godown_quantity != '':
                                opening_godown_quantity_dict = json.loads(opening_godown_quantity)
                                opening_godown_qty_data = opening_godown_quantity_dict.get('newData')
                                
                                item_godown_formset_data = {}
                                for key , value in opening_godown_qty_data.items():
                                    form_set_id = key.split('_')[-1]

                                    new_data_get = opening_godown_qty_data.get(key)
                                    print(new_data_get)

                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-TOTAL_FORMS'] = str(len(opening_godown_qty_data))
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-INITIAL_FORMS'] =  str(0)
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-MIN_NUM_FORMS'] =  str(0)
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-MAX_NUM_FORMS'] =  str(1000)
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_godown_id'] = new_data_get.get('godownData')
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_quantity'] = new_data_get.get('qtyData')
                                    item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_rate'] = new_data_get.get('rateData')
                                
                                #formset
                                new_godown_opening_formsets = OpeningShadeFormSetupdate(item_godown_formset_data, prefix='opening_shade_godown_quantity_set')

                                for form in new_godown_opening_formsets:
                                    if form.is_valid():
                                        form_instance = form.save(commit = False)
                                        
                                        form_instance.opening_purchase_voucher_godown_item = shade_form_instance
                                        form_instance.save()
                                
                                    

                            form_instance = form.save(commit = False)
                            form_instance.save()

            messages.success(request,'Item updated successfully')
            return redirect('item-list')
        
    return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
                                                                 'packaging_material_all':packaging_material_all,
                                                                 'fab_finishes':fab_finishes,
                                                                 'form':form,
                                                                 'formset': formset})


def openingquantityformsetpopup(request,parent_row_id=None,primary_key=None):
    print('POST',request.POST)

    godowns =  Godown_raw_material.objects.all()

    formset = None
    shade_instance = None
    
    if parent_row_id is not None and primary_key is not None:
        shade_instance = get_object_or_404(item_color_shade,pk=primary_key)
        formset = OpeningShadeFormSetupdate(request.POST or None, instance = shade_instance, prefix = "opening_shade_godown_quantity_set")


    elif primary_key is None and parent_row_id is not None:

        decoded_data = False

        #get data from session # change or remove this part
        encoded_data = request.GET.get('data')
        
        if encoded_data:
            decoded_data = json.loads(urllib.parse.unquote(encoded_data))
            new_row_data = decoded_data.get('newData', {})
            initial_data_backend = []
            print('new_row_data',new_row_data)
            
            for key, value in new_row_data.items():
                initial_data_backend.append({
                        "opening_godown_id": int(value['godownData']),
                        "opening_quantity": float(value['qtyData']),
                        "opening_rate": float(value['rateData'])})

            print(initial_data_backend)

            total_forms = len(initial_data_backend)
            opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_godown_id','opening_quantity','opening_rate'], extra=total_forms, can_delete=True)   # when using modelformset need to add can_delete = True or delete wont be added in for
            formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),initial=initial_data_backend, prefix = "opening_shade_godown_quantity_set")
            

        else:
            opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_rate','opening_quantity','opening_godown_id'], extra=1, can_delete=True)            
            formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),prefix = "opening_shade_godown_quantity_set")
    
    if request.method == 'POST':
        if primary_key is not None:
            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        print(form.cleaned_data)
                        old_opening_quantity = form.instance.opening_quantity
                        form_instance = form.save(commit=False)
                        form_instance.old_opening_g_quantity = old_opening_quantity 
                        form_instance.save()

        

    print(formset)
    return render(request,'product/opening_godown_qty.html',{'formset':formset,'godowns':godowns ,"parent_row_id":parent_row_id, 'primary_key':primary_key,'shade_instance':shade_instance})




def openingquantityformsetpopupajax(request):
    itemValue_get = request.GET.get('itemValue')
    primary_key_id_get = request.GET.get('primary_key_id')        

    if itemValue_get is not None and primary_key_id_get != '':
        popup_url = reverse('opening-godown-qty-pk', args=[primary_key_id_get,itemValue_get])

    elif itemValue_get is not None:
        popup_url = reverse('opening-godown-qty', args=[itemValue_get])

    else:
        popup_url = None
    
    return JsonResponse({'popup_url':popup_url})




def item_delete(request, pk):
    
    try:
        item_pk = get_object_or_404(Item_Creation,pk = pk)
        item_pk.delete()
        messages.success(request,f'Item {item_pk.item_name} was deleted')
    except IntegrityError as e:
        messages.error(request, f'Cannot delete {item_pk.item_name} because it is referenced by other objects.')
    return redirect('item-list')



def item_create_dropdown_refresh_ajax(request):
    print(request.GET.get('gst_change'))
    print('TEST')
    return JsonResponse('TEST')

#_____________________Item-Views-end_______________________

#_____________________Color-start________________________



def color_create_update(request, pk=None):


    if request.path == '/simple_colorcreate_update/':
        template_name = 'product/color_create_update.html'
        title = 'Create Color'

    elif request.path == f'/simple_colorcreate_update/{pk}':
        template_name = 'product/color_create_update.html'
        title = 'Update Color'

    elif request.path == '/colorcreate_update/':
        template_name = "product/create_color_modal.html"
        title = 'Colors'

    elif request.path == '/color_popup/':
        template_name = "product/color_popup.html"
        title = 'Create Colors'
    
    color = Color.objects.all()

    if pk:
        instance = get_object_or_404(Color, pk = pk)
    else:
        instance = None

    form = ColorForm(instance=instance)
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            # need to add a verification if getting request from simple form or from modal for save redirection 
            
            if 'save' in request.POST and request.path == '/simple_colorcreate_update/' or request.path == f'/simple_colorcreate_update/{pk}':
                if instance:
                    messages.success(request, 'Color updated successfully.')
                else:
                    messages.success(request, 'Color created successfully.')
                
                return redirect('simplecolorlist')
            
            elif 'save' in request.POST and template_name == "product/color_popup.html":

                color_all = Color.objects.all().values('id','color_name')
                messages.success(request, 'Color created successfully.')
                return JsonResponse({'color_all':list(color_all)}) 
        else:
            print(form.errors)
            return render(request, template_name,{'title': title,'form': form,'colors':color})

    return render(request, template_name , {'title': title, 'form': form, 'colors':color})
        

def color_delete(request, pk):
    
    try:
        product_color = get_object_or_404(Color,pk=pk)
        product_color.delete()
        messages.success(request,f'Color {product_color.color_name} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {product_color.color_name} because it is referenced by other objects.')
    return redirect('simplecolorlist')



#_____________________Color-end________________________



#_______________________fabric group start___________________________________



def item_fabric_group_create_update(request, pk = None):
    fab_group_all = Fabric_Group_Model.objects.all()

    if pk:
        item_fabric_pk =  get_object_or_404(Fabric_Group_Model,pk=pk)
        instance = item_fabric_pk
        title = 'Fabric Group Update'
    else:
        form = ItemFabricGroup()
        instance = None
        title = 'Fabric Group Create'
    

    if request.path == '/itemfabricgroupcreateupdate/':
        template_name = 'product/item_fabric_group_create_update.html'

    elif request.path == '/fabric_popup/':
        template_name = 'product/fabric_popup.html'

    elif request.path == f'/itemfabricgroupcreateupdate/{pk}':
        template_name = 'product/item_fabric_group_create_update.html'

    form = ItemFabricGroup(instance=instance)
    if request.method == 'POST':
        form = ItemFabricGroup(request.POST, instance=instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request,'Fabric group updated sucessfully.')
            else:
                messages.success(request,'Fabric group created sucessfully.')

            if 'save' in request.POST and template_name == 'product/item_fabric_group_create_update.html':
                return redirect('item-fabgroup-create-list')

            elif 'save' in request.POST and template_name == 'product/fabric_popup.html':
                Fabric_Group_all = Fabric_Group_Model.objects.all().values('id','fab_grp_name')
                return JsonResponse({'Fabric_Group_all':list(Fabric_Group_all)})

        else:
            print(form.errors)
            return render(request,template_name,{'title': title,"fab_group_all":fab_group_all,
                                                                                  'form':form})


    return render(request,template_name,{'title': title, "fab_group_all":fab_group_all,
                                                                          'form':form})





def item_fabric_group_delete(request,pk):
    try:
        item_fabric_pk = get_object_or_404(Fabric_Group_Model,pk=pk)
        item_fabric_pk.delete()
        messages.success(request,f'Fabric group {item_fabric_pk.fab_grp_name} was deleted')

    except IntegrityError as e:
        messages.error(request,f'Cannot delete {item_fabric_pk.fab_grp_name} because it is referenced by other objects.')
    
    return redirect('item-fabgroup-create-list')


#_______________________fabric group end___________________________________

#_______________________Unit Name Start____________________________________

def unit_name_create_update(request,pk=None):
    
    unit_name_all = Unit_Name_Create.objects.all()

    if pk:
        unit_name_pk = get_object_or_404(Unit_Name_Create,pk=pk)
        instance = unit_name_pk
        title = 'Unit Update'
    else:
        instance= None
        title = 'Unit Create'

    form = UnitName(instance = instance)

    if request.path == '/unitnamecreate/':
        template_name = 'product/unit_name_create_update.html'

    elif request.path == '/units_popup/':
        template_name = 'product/units_popup.html'
    
    elif request.path == f'/unitnameupdate/{pk}':
        template_name = 'product/unit_name_create_update.html'

    if request.method == 'POST':
        form = UnitName(request.POST, instance=instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request,'Unit updated sucessfully.')
            else:
                messages.success(request,'Unit created sucessfully.')

            
            if 'save' in request.POST and template_name == 'product/unit_name_create_update.html':
                return redirect('unit_name-create_list')

            elif 'save' in request.POST and template_name == 'product/units_popup.html':
                Unit_Name_all_values = Unit_Name_Create.objects.all().values('id','unit_name')
                return JsonResponse({'Unit_Name_all_values':list(Unit_Name_all_values)})

        else:
            print(form.errors)
            return render(request, template_name, {'title': title,'form':form,"unit_name_all":unit_name_all})
        
    else:
        return render(request, template_name, {'title':title,'form':form,"unit_name_all":unit_name_all})





def unit_name_delete(request,pk):
    try:
        unit_name_pk = get_object_or_404(Unit_Name_Create,pk=pk)
        unit_name_pk.delete()
        messages.success(request,f'Unit name {unit_name_pk.unit_name} was deleted.')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {unit_name_pk.unit_name} because it is referenced by other objects.')
    return redirect('unit_name-create_list')


#________________________Unit Name End_______________________________________





#_________________________Accounts start___________________________

def account_sub_group_create(request):
    print(request.POST)
    main_grp = AccountGroup.objects.all()
    form = account_sub_grp_form()
    if request.method == 'POST':
        form = account_sub_grp_form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account sub-group created sucessfully')
            if 'save' in request.POST:
                return redirect('account_sub_group-list')
            elif 'save_and_add_another' in request.POST:
                return redirect('account_sub_group-create')
        else:
            print(form.errors)
            return render(request,'product/acc_sub_grp_create_update.html', {'main_grp':main_grp,
                                                                             'title':'Account Sub-Group Create',
                                                                             'form':form})
        
    return render(request,'product/acc_sub_grp_create_update.html', {'main_grp':main_grp, 
                                                                     'title':'Account Sub-Group Create',
                                                                     'form':form})


def account_sub_group_update(request, pk):
    main_grp = AccountGroup.objects.all()
    group = get_object_or_404(AccountSubGroup ,pk=pk)
    form = account_sub_grp_form(instance = group)
    if request.method == 'POST':
        form = account_sub_grp_form(request.POST, instance = group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account sub-group updated sucessfully')
            return redirect('account_sub_group-list')
        else:
            print(form.errors)
            return render(request, 'product/acc_sub_grp_create_update.html', {'main_grp':main_grp,
                                                                              'title':'Account Sub-Group Update',
                                                                              'form':form})
        
    return render(request, 'product/acc_sub_grp_create_update.html', {'main_grp':main_grp,
                                                                      'title':'Account Sub-Group Update',
                                                                      'form':form})


def account_sub_group_list(request):
    groups = AccountSubGroup.objects.select_related('acc_grp').all()
    return render(request,'product/acc_sub_grp_list.html', {"groups":groups})


def account_sub_group_delete(request, pk):
    try:
        group = get_object_or_404(AccountSubGroup ,pk=pk)
        group.delete()
        messages.success(request,f'Account Sub Group {group.account_sub_group} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {group.account_sub_group} because it is referenced by other objects.')
    return redirect('account_sub_group-list')



def stock_item_create_update(request,pk=None):

    if pk:
        instance = get_object_or_404(StockItem ,pk=pk)
        title = 'Stock Item Update'
    else:
        instance = None
        title = 'Stock Item Update'


    stocks = StockItem.objects.all()
    accsubgrps = AccountSubGroup.objects.all()
    form = StockItemForm(instance=instance)
    if request.method == 'POST':
        form = StockItemForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request, 'Stock item updated sucessfully')
            else:
                messages.success(request, 'Stock item created sucessfully')

            if 'save' in request.POST:
                return redirect('stock-item-create')

        else:
            print(form.errors)
            return render(request,'product/stock_item_create_update.html', {'title':'Stock Item Create',
                                                                            'accsubgrps':accsubgrps,
                                                                            'form':form,'stocks':stocks})
    
    
    return render(request,'product/stock_item_create_update.html', {'title':'Stock Item Create',
                                                                    'accsubgrps':accsubgrps,
                                                                    'form':form,'stocks':stocks})





def stock_item_delete(request, pk):
    try:
        stock = get_object_or_404(StockItem ,pk=pk)
        stock.delete()
        messages.success(request,f'Stock Item {stock.stock_item_name} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {stock.stock_item_name} because it is referenced by other objects.')        
    return redirect('stock-item-create')


@transaction.atomic
def ledgercreate(request):
    under_groups = AccountSubGroup.objects.all()
    form = LedgerForm()
    if request.method == 'POST':
        form = LedgerForm(request.POST)
        if form.is_valid():
            ledger_instance = form.save(commit = False) #ledger_instance this has the instance of ledger form
            form.save()
            open_bal_value = form.cleaned_data['opening_balance']
            debit_credit_value = form.cleaned_data['Debit_Credit']

            if debit_credit_value == 'Debit':
                account_credit_debit_master_table.objects.create(ledger = ledger_instance, voucher_type = 'Ledger' ,debit= open_bal_value)

            elif debit_credit_value == 'Credit':
                account_credit_debit_master_table.objects.create(ledger = ledger_instance, voucher_type = 'Ledger',credit= open_bal_value)
            
            messages.success(request,'Ledger Created')
            return redirect('ledger-list')
        
        else:

            return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create'})
    

    return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create'})
    

@transaction.atomic
def ledgerupdate(request,pk):
    under_groups = AccountSubGroup.objects.all()
    
    Ledger_pk = get_object_or_404(Ledger,pk = pk)
    ledgers = Ledger_pk.transaction_entry.all() #get all transactions related instances to the ledger

    Opening_ledger = ledgers.filter(voucher_type ='Ledger').first() # filter the first related instance for only ledger as voucher type
    form = LedgerForm(instance = Ledger_pk)
    opening_balance = 0

    if form.instance.Debit_Credit == 'Debit':            # if form instance has Debit 
        opening_bal = Opening_ledger.debit               # get the data from the debit side of transaction_entry
        opening_balance = opening_balance + opening_bal  # and store it in opening_balance variable

    elif form.instance.Debit_Credit == 'Credit':         # if form instance has Credit
        opening_bal = Opening_ledger.credit              # get the data from the credit side of transaction_entry
        opening_balance = opening_balance + opening_bal  # and store it in opening_balance variable

    else:
        messages.error(request,' Error with Credit Debit ')
    
    if request.method == 'POST':
        
        form = LedgerForm(request.POST, instance = Ledger_pk)
        name_for_message = request.POST['name']
        if form.is_valid():
            form.save()

            if request.POST['Debit_Credit'] == 'Debit':
                Opening_ledger.debit = request.POST['opening_balance']
                Opening_ledger.credit = 0
                Opening_ledger.save()

            if request.POST['Debit_Credit'] == 'Credit':
                Opening_ledger.credit = request.POST['opening_balance']
                Opening_ledger.debit = 0
                Opening_ledger.save()
            
            messages.success(request, f'Ledger of {name_for_message} Updated')
            return redirect('ledger-list')
        else:
            
            return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Update', 'open_bal':opening_balance})
    
    return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Update', 'open_bal':opening_balance})



def ledgerlist(request):
    ledgers = Ledger.objects.select_related('under_group').all()
    return render(request, 'accounts/ledger_list.html', {'ledgers':ledgers})



def ledgerdelete(request, pk):
    try:
        Ledger_pk = get_object_or_404(Ledger ,pk=pk)
        Ledger_pk.delete()
        messages.success(request,f'ledger of {Ledger_pk.name} was deleted')
    except Exception as e:
        messages.error(request,f'Cannot delete {Ledger_pk.name} because it is referenced by other objects.')
    return redirect('ledger-list')




#_________________________Accounts end___________________________

#________________________godown start______________________________




def godowncreate(request):
    if request.method == 'POST':

        godown_name =  request.POST['godown_name']
        godown_type = request.POST['Godown_types']
        if godown_type == 'Raw Material':
            godown_raw = Godown_raw_material(godown_name_raw=godown_name) #instance of Godown_raw_material
            godown_raw.save()  #save the instance to db 
            messages.success(request,'Raw material godown created.')

            if 'save' in request.POST:
                return redirect('godown-list')
            elif 'save_and_add_another' in request.POST:
                return redirect('godown-create')
        
        elif godown_type == 'Finished Goods':
            godown_finished = Godown_finished_goods(godown_name_finished=godown_name) #instance of Godown_finished_goods
            godown_finished.save() #save the instance to db 
            messages.success(request,'Finished goods godown created.')

            if 'save' in request.POST:
                return redirect('godown-list')
            elif 'save_and_add_another' in request.POST:
                return redirect('godown-create')
        else:
            messages.error(request,'Error Selecting Godown.')
            return redirect('godown-list')
            
    return render(request,'misc/godown_create.html')

    

def godownupdate(request,str,pk):
    if str == 'finished':
        godown_type = 'Finished Goods'
        finished_godown_pk = get_object_or_404(Godown_finished_goods, pk=pk)
        instance_data = finished_godown_pk.godown_name_finished
        if request.method == 'POST':
            godown_name =  request.POST['godown_name']
            finished_godown_pk.godown_name_finished = godown_name
            finished_godown_pk.save()
            messages.success(request,'Finished goods godown updated.')
            return redirect('godown-list')
        
    elif str == 'raw':
        godown_type = 'Raw Material'
        raw_godown_pk = get_object_or_404(Godown_raw_material , pk=pk)
        instance_data = raw_godown_pk.godown_name_raw
        if request.method == 'POST':
            godown_name =  request.POST['godown_name']
            raw_godown_pk.godown_name_raw = godown_name
            raw_godown_pk.save()
            messages.success(request,'Raw material godown updated.')
            return redirect('godown-list')
    else:
        messages.error(request,'error in godownupdate str variable')
    
    context = {
        'instance_data': instance_data,
        'godown_type': godown_type
    }
    print(context)
    return render(request,'misc/godown_update.html', context)



def godownlist(request):
    godowns_raw = Godown_raw_material.objects.all()
    godowns_finished = Godown_finished_goods.objects.all()
    return render(request,'misc/godown_list.html',{'godowns_raw':godowns_raw, 
                                                   'godowns_finished':godowns_finished})



def godowndelete(request,str,pk):
    if str == 'finished':
        try:
            finished_godown_pk = get_object_or_404(Godown_finished_goods, pk=pk)
            finished_godown_pk.delete()
            messages.success(request,f'Finished Goods Godown {finished_godown_pk.godown_name_finished} was deleted')
            
        except Exception as e:
            messages.error(request,f'Cannot delete {finished_godown_pk.godown_name_finished} because it is referenced by other objects. ')
            

    elif str == 'raw':
        try:
            raw_godown_pk = get_object_or_404(Godown_raw_material, pk=pk)
            raw_godown_pk.delete()
            messages.success(request,f'Raw Material Godown - {raw_godown_pk.godown_name_raw} was deleted')
            
        except Exception as e:
            messages.error(request,f'Cannot delete {raw_godown_pk.godown_name_raw} because it is referenced by other objects. ')
            
    else:
        messages.error(request, f'Error Deleting Godowns')
    return redirect('godown-list')
    
    


#_________________________godown end______________________________

#__________________________stock transfer start__________________________



# RawStockTransfer
def stocktransfer(request):
    print(request.POST)
    current_date = now().date()
    raw_godowns = Godown_raw_material.objects.all()
    rawstocktransferlist = RawStockTransfer.objects.all()
    #godowns - one to many - godownitems - many to one - item_shades - many to one - items
    if request.method == 'GET':
        selected_source_godown_id = request.GET.get('selected_godown_id') 
        selected_source_godown_items = item_godown_quantity_through_table.objects.filter(godown_name=selected_source_godown_id)

        # items in the selected godown 
        items_in_godown = {}
        for items in selected_source_godown_items:
            item = items.Item_shade_name
            item_name =  item.items.item_name
            item_id = item.items.id
            items_in_godown[item_id] = item_name

        # shades of the selected item from the godown 
            
        #get the selected item
        item_name_value = request.GET.get('item_value')

        #selected godown
        item_color_godown = request.GET.get('selectedValueGodown')

        # get the shade of the selected item
        item_shades_of_selected_item = item_color_shade.objects.filter(items=item_name_value)

        item_shades = {}
        items_shade_quantity_in_godown = {}

        #loop through the itemshade of item   
        for x in item_shades_of_selected_item:

            # in the through table to with the selected shade of the selected item and selected godown
            shades_of_item_in_selected_godown = item_godown_quantity_through_table.objects.filter(godown_name = item_color_godown, Item_shade_name=x.id)

            # loop through the filtered queryset of shades in the godown and make 
            # item_shade dict to send in front end 
            for x in shades_of_item_in_selected_godown:
                shade_name = x.Item_shade_name.item_shade_name
                shade_id = x.Item_shade_name.id
                item_shades[shade_id] = shade_name

                #quantity of shade in godown
                item_id = x.Item_shade_name.id
                items_shade_quantity_in_godown[item_id] = x.quantity

        item_color = None
        item_per = None

        if item_name_value is not None:
            item_name_value = int(item_name_value)

            # get the item 
            items =  get_object_or_404(Item_Creation ,id = item_name_value)
        
            item_color = items.Item_Color.color_name
            item_per = items.unit_name_item.unit_name

        
        shade_quantity = 0
        selected_shade = request.GET.get('selected_shade_id')
        selected_godown = request.GET.get('godown_id')
       
        if selected_shade is not None and selected_godown is not None:
            selected_shade = int(selected_shade)
            selected_source_godown_id = int(selected_godown)

            quantity_get = item_godown_quantity_through_table.objects.filter(Item_shade_name = selected_shade, godown_name =selected_source_godown_id).first()
            shade_quantity  = quantity_get.quantity


        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'items_in_godown': items_in_godown, 'item_shades':item_shades,
                                'item_color':item_color,'item_per':item_per, 'shade_quantity':shade_quantity,'items_shade_quantity_in_godown':items_shade_quantity_in_godown })
        

        else:
             return render(request,'misc/stock_transfer.html',{'raw_godowns':raw_godowns,'transferlist':rawstocktransferlist,'current_date':current_date})


    if request.method == 'POST':
        source_godown =request.POST.get('source_godown')
        target_godown = request.POST.get('target_godown')
        item_name_transfer = request.POST.get('name')
        item_color_transfer = request.POST.get('color')
        item_shade_transfer = request.POST.get('shades')
        item_quantity_transfer = int(request.POST.get('quantity'))
        item_unit_transfer = request.POST.get('per')
        remarks = request.POST.get('remark')

        if source_godown is not None and target_godown is not None and source_godown != target_godown :
            try:
                source_godown_raw =  Godown_raw_material.objects.get(id=source_godown)
                target_godown_raw = Godown_raw_material.objects.get(id=target_godown)
                item_name_transfer_raw = Item_Creation.objects.get(id=item_name_transfer)
                item_shade_transfer_raw = item_color_shade.objects.get(id=item_shade_transfer)

                # filter the source godown
                source_g = item_godown_quantity_through_table.objects.get(godown_name=source_godown, Item_shade_name=item_shade_transfer)

                #filter the destination godown
                destination_g = item_godown_quantity_through_table.objects.get(godown_name=target_godown, Item_shade_name=item_shade_transfer)
            
                with transaction.atomic():
                    #substract the quantity from source 
                    source_g.quantity = source_g.quantity - item_quantity_transfer  
                    source_g.save()

                    # add the quantity to the destination
                    destination_g.quantity = destination_g.quantity + item_quantity_transfer
                    destination_g.save()

            
                    RawStockTransfer.objects.create(source_godown=source_godown_raw,destination_godown=target_godown_raw,
                                            item_name_transfer=item_name_transfer_raw,item_color_transfer=item_color_transfer,
                                            item_shade_transfer=item_shade_transfer_raw,
                                            item_quantity_transfer=item_quantity_transfer,
                                            item_unit_transfer=item_unit_transfer, remarks=remarks)
                messages.success(request,f' Item {item_name_transfer_raw}(Quantity->{item_quantity_transfer}) transfered from {source_godown_raw} to {target_godown_raw}.')
                return redirect('stock-transfer') 
        
            

            except item_godown_quantity_through_table.DoesNotExist:
                with transaction.atomic():
                    #substract the quantity from source 
                    source_g.quantity = source_g.quantity - item_quantity_transfer
                    source_g.save()
            
                    # Retrieve the godown instances
                    target_godown_instance = Godown_raw_material.objects.get(id=target_godown)
                    item_shade_transfer_instance = item_color_shade.objects.get(id=item_shade_transfer)
            

                    # Create a new entry for the item shade in the destination godown
                    new_entry = item_godown_quantity_through_table.objects.create(
                    godown_name=target_godown_instance,
                    Item_shade_name=item_shade_transfer_instance,
                    quantity=item_quantity_transfer)
            
                    RawStockTransfer.objects.create(source_godown=source_godown_raw,destination_godown=target_godown_raw,
                                            item_name_transfer=item_name_transfer_raw,item_color_transfer=item_color_transfer,
                                            item_shade_transfer=item_shade_transfer_raw,
                                            item_quantity_transfer=item_quantity_transfer,
                                            item_unit_transfer=item_unit_transfer, remarks=remarks)
                    
                    messages.success(request,f' Item {item_name_transfer_raw}(Quantity->{item_quantity_transfer}) created and transfered from {source_godown_raw} to {target_godown_raw}')
                    return redirect('stock-transfer') #add message new item added in godown with quanitiy
        else:
            messages.error(request, 'Source and Target godown is same.')
            return redirect('stock-transfer')           
        

def stocktransferreport(request):
    rawstocktransferlist = RawStockTransfer.objects.all()
    return render(request,'misc/stock_transfer_list.html',{'transferlist':rawstocktransferlist})


#__________________________stock transfer end__________________________



#__________________________purchase voucher start__________________________



def purchasevouchercreateupdate(request, pk=None):
    item_name_searched = Item_Creation.objects.all()
    if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':


        #get the purchase invoice for updating the form 
        if pk:
            purchase_invoice_instance = get_object_or_404(item_purchase_voucher_master,pk=pk)
            item_formsets_change = purchase_voucher_items_formset_update(request.POST or None, instance=purchase_invoice_instance)
        
        else:
            purchase_invoice_instance = None
            item_formsets_change = purchase_voucher_items_formset(request.POST or None, instance=purchase_invoice_instance)

        items_formset = item_formsets_change
        Purchase_gst = gst.objects.all()

        for forms in items_formset.forms:
            godown_items_formset = purchase_voucher_items_godown_formset()

        raw_material_godowns = Godown_raw_material.objects.all()

        master_form  = item_purchase_voucher_master_form(instance=purchase_invoice_instance)
        
        account_sub_grp = AccountSubGroup.objects.filter(account_sub_group__icontains='Sundray Creditor(we buy)').first()
        
        if account_sub_grp is not None:
            
            party_names = Ledger.objects.filter(under_group=account_sub_grp.id)
        else:
            party_names = ''
    
    try:

        party_gst_no = ''
        selected_party_name = request.GET.get('selected_party_name')
        if selected_party_name is not None:
            ledger_instance = Ledger.objects.filter(id = selected_party_name).first()
            party_gst_no = party_gst_no + ledger_instance.Gst_no

        item_value = request.GET.get('item_value')
        #item values
        item_color_out = ''
        item_per_out = ''
        item_gst_out = 0
    
        if item_value is not None: 
            item_value = int(item_value)
            item = Item_Creation.objects.get(id = item_value)
            item_color = item.Item_Color.color_name
            item_color_out =  item_color_out + item_color
            item_per = item.unit_name_item.unit_name
            item_per_out = item_per_out + item_per
            item_gst = item.Item_Creation_GST.gst_percentage
            item_gst_out = item_gst_out + item_gst
        
        # filter out item shades
        item_shades = item_color_shade.objects.filter(items = item_value)

        item_shades_dict = {}
        item_shades_total_quantity_dict = {}
        
        for shade in item_shades:
            item_shades_dict[shade.id] = shade.item_shade_name
            
            godown_shade_quantity = 0
            shade_godowns =  item_godown_quantity_through_table.objects.filter(Item_shade_name = shade)
            for godown in shade_godowns:
                godown_shade_quantity = godown_shade_quantity + godown.quantity
            item_shades_total_quantity_dict[shade.id] = godown_shade_quantity
        
    except Exception as e:
        print(f'exception occoured {e}')
    
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
             return JsonResponse({'item_color': item_color_out , 'item_shade': item_shades_dict,
                                  "item_per":item_per_out, 'item_shades_total_quantity_dict':item_shades_total_quantity_dict,
                                  'item_gst_out':item_gst_out,'party_gst_no':party_gst_no,})

    if request.method == 'POST':
        print(request.POST)
        try:
            with transaction.atomic(): #start a database transaction
                #create a form instance for main form
                master_form = item_purchase_voucher_master_form(request.POST,instance=purchase_invoice_instance)

                #create a formset instance for form items in invoice
                items_formset = item_formsets_change

                #create a formset instance for godowns in form items
                godown_items_formset = purchase_voucher_items_godown_formset(request.POST, prefix='shade_godown_items_set')

                #filter out only the forms which are changed or added 
                items_formset.forms = [form for form in items_formset.forms] # if form.has_changed()  

                print('items_formset.forms',items_formset.deleted_forms)
                if master_form.is_valid() and items_formset.is_valid():
                    # Save the master form
                    master_instance = master_form.save()

                    # Check for items marked for deletion and delete them 
                    # delete wont work after default as we are not saving items_formset instead we are saving  in the formsets individually
                    # items_formset.deleted_forms has the forms marked for deletion
                    for form in items_formset.deleted_forms:
                        if form.instance.pk:
                            #boolen to check if the instance was directly deleted or via models.CASCADE later used in signals 
                            form.instance.deleted_directly = True
                            form.instance.delete()

                    all_purchase_temp_data = []
                    # loop through each form in formset to attach the instance of master_instance with each form in the formset
                    for form in items_formset:
                        if form.is_valid():

                            # form.cleaned_data and item_formset.cleaned_data have same data but formset.cleaned_data is in a form of list of form.cleaned data
                            if not form.cleaned_data.get('DELETE'):
                                items_instance = form.save(commit=False)
                                items_instance.item_purchase_master = master_instance
                                items_instance.save()
                                
                                form_prefix_number = form.prefix[-1] #gives the prefix number of the current iteration of the form
                                
                                #get the pk of that item row and get the unique id if any present 
                                unique_id_no = request.POST.get(f'item_unique_id_{form_prefix_number}')
                                primary_key = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-id')
                                
                                #check if pk is not there in the formset which means form is newly created then its been saved in temp godown with unique id 
                                if primary_key == '' or primary_key == None: 
                                    purchase_voucher_temp_data = shade_godown_items_temporary_table.objects.filter(unique_id=unique_id_no)
                                    for data in purchase_voucher_temp_data:
                                        all_purchase_temp_data.append(data)
                                
                                    godown_temp_data = {}
                                    form_set_id = 0
                                    for temp_godown_row_data in purchase_voucher_temp_data:
                                        godown_temp_data[f'shade_godown_items_set-TOTAL_FORMS'] = str(len(purchase_voucher_temp_data))
                                        godown_temp_data[f'shade_godown_items_set-INITIAL_FORMS'] =  str(0)
                                        godown_temp_data[f'shade_godown_items_set-MIN_NUM_FORMS'] =  str(0)
                                        godown_temp_data[f'shade_godown_items_set-MAX_NUM_FORMS'] =  str(1000)
                                        godown_temp_data[f'shade_godown_items_set-{form_set_id}-godown_id'] = temp_godown_row_data.godown_id
                                        godown_temp_data[f'shade_godown_items_set-{form_set_id}-quantity'] = temp_godown_row_data.quantity
                                        godown_temp_data[f'shade_godown_items_set-{form_set_id}-rate'] = temp_godown_row_data.rate
                                        godown_temp_data[f'shade_godown_items_set-{form_set_id}-amount'] = temp_godown_row_data.amount
                                        form_set_id =  form_set_id + 1
                                    
                                    godown_items_formset = purchase_voucher_items_godown_formset(godown_temp_data, prefix='shade_godown_items_set')
                                    saved_data_to_delete = 0
                                    for godown_form in godown_items_formset:
                                        if godown_form.is_valid():
                                            godown_instance = godown_form.save(commit = False)
                                            godown_instance.purchase_voucher_godown_item = items_instance #save form to permanant table with link to parent table pk
                                            godown_instance.save()
                                            saved_data_to_delete = saved_data_to_delete + 1
                                            print('Data-saved')
                                        else:
                                           
                                            purchase_voucher_temp_data.delete()

                                    if saved_data_to_delete == form_set_id:
                                        purchase_voucher_temp_data.delete()


                                # first check if quantity is updated in invoice database 
                                godown_item_quantity = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-jsonDataInputquantity')
                               
                                if godown_item_quantity != '':
                                    voucher_row_godown_data = json.loads(godown_item_quantity)
                                    
                                    parent_row_prefix_id = voucher_row_godown_data.get('parent_row_prefix_id')

                                    if parent_row_prefix_id == form_prefix_number:

                                        new_row = voucher_row_godown_data.get('newRow')
                                        new_rate = float(voucher_row_godown_data.get('all_Rate'))
                                        row_item = items_instance.item_shade.id
                                        Item_instance =  item_color_shade.objects.get(id = row_item)

                                        for key, value in new_row.items():
                                            godown_id = int(value['gId'])    # new godown id
                                            updated_quantity = value['jsonQty']   # new quantity

                                            # Check for empty string specifically
                                            godown_old_id = value.get('popup_old_id', None)   # old_godown_id 
                                            if godown_old_id == '':
                                                godown_old_id = None

                                            if godown_old_id != '' and godown_old_id is not None:
                                                godown_old_id = int(godown_old_id)   

                                            popup_row_id = value.get('popup_row_id', None)  # godown_row_id 
                                            if popup_row_id == '':
                                                popup_row_id = None
                                        
                                            #logic for new row added in godownpopup or godown is the same as old only quantity is updated
                                            if godown_old_id == None or godown_old_id == godown_id:
                                                
                                                godown_instance = Godown_raw_material.objects.get(id = godown_id)
                                                Item, created = item_godown_quantity_through_table.objects.get_or_create(godown_name = godown_instance,Item_shade_name = Item_instance)
                                                
                                                if popup_row_id == None or popup_row_id == '' :
                                                    initial_quantity = 0

                                                else:
                                                    initial_quantity = shade_godown_items.objects.get(pk = popup_row_id)
                                                    initial_quantity = initial_quantity.quantity
                                                
                                                qty_to_update = updated_quantity - initial_quantity
                                                
                                                Item.quantity = Item.quantity + qty_to_update
                                                Item.item_rate = new_rate
                                                Item.save()
                                            
                                            # logic for saved item row and godowns(godowns with pk) and godown has changed and has old godown id 
                                            if godown_old_id != None:
                                                
                                                godown_old_id = int(godown_old_id) 
                                                godown_instance_old = Godown_raw_material.objects.get(id = godown_old_id)

                                                godown_new_id = int(godown_id)
                                                godown_instance_new = Godown_raw_material.objects.get(id = godown_new_id)

                                                # logic if godown has changed in godown popup
                                                if godown_old_id != godown_new_id:
                                                    old_quantity_get = shade_godown_items.objects.get(pk = popup_row_id)
                                                    old_quantity = old_quantity_get.quantity

                                                    old_godown_through_row = item_godown_quantity_through_table.objects.get(godown_name = godown_instance_old,Item_shade_name=Item_instance)

                                                    old_godown_through_row.quantity = old_godown_through_row.quantity - old_quantity
                                                    old_godown_through_row.save()

                                                    new_godown_through_row, created  = item_godown_quantity_through_table.objects.get_or_create(godown_name = godown_instance_new,Item_shade_name=Item_instance)
                                                    
                                                    # if the row is present 
                                                    if new_godown_through_row:
                                                        new_quantity_c = new_godown_through_row.quantity
                                                    else:
                                                        # else if row is not present 
                                                        new_quantity_c = 0

                                                    new_godown_through_row.quantity = new_quantity_c + updated_quantity
                                                    new_godown_through_row.save()


                                #popupvoucherfunction post initilization
                                popup_godowns_exists = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-popupData')
                                old_item_shade = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-old_item_shade')
                                
                                if popup_godowns_exists != '':
                                    popup_godown_data = json.loads(popup_godowns_exists)
                                    print('popup_godown_data',popup_godown_data)
                                    row_prefix_id = popup_godown_data.get('prefix_id')

                                    if row_prefix_id == form_prefix_number:
                                        
                                        shade_id = int(popup_godown_data.get('shade_id'))
                                        prefix_id =  int(popup_godown_data.get('prefix_id'))
                                        primarykey = int(popup_godown_data.get('primary_id'))
                                        old_item_shade = int(old_item_shade)
                                        
                                        #function to update popup data on main submit only 
                                        purchasevoucherpopupupdate(popup_godown_data,shade_id,prefix_id,primarykey,old_item_shade)
                                        
                        else:
                            print('form1',form.errors)
                            
                    print('all_data', all_purchase_temp_data)
                    return redirect('purchase-voucher-list')
                else:
                    #deleting session data(unique keys and boolien) if any and deleting record of those unique keys on refresh
                    if 'temp_data_exists' in request.session and 'temp_uuid' in request.session: 
                        temp_data_exists_bool = request.session['temp_data_exists']
                        temp_uuids = request.session['temp_uuid']
                        del request.session['temp_data_exists']
                        del request.session['temp_uuid']
                        for data in temp_uuids:
                            temp_uuids_data =  shade_godown_items_temporary_table.objects.filter(unique_id=data)
                            temp_uuids_data.delete()
                    print('MF',master_form.errors)
                    print('IF',items_formset.errors)
                    return redirect('purchase-voucher-list')
            
        except Exception as e:
            print('an error occoured-test',e)
            messages.error(request,f'An error occoured{e} godown temporary data deleted')
            
        finally:
                # Delete temporary data if there a a flag which was set while creating temp data
                # this will ensure the table will be be deleted by someone who created some temp data   
                #deleting session data(unique keys and boolien) if any and deleting record of those unique keys on refresh
                if 'temp_data_exists' in request.session and 'temp_uuid' in request.session: 
                    temp_data_exists_bool = request.session['temp_data_exists']
                    temp_uuids = request.session['temp_uuid']
                    del request.session['temp_data_exists']
                    del request.session['temp_uuid']
                    for data in temp_uuids:
                        temp_uuids_data = shade_godown_items_temporary_table.objects.filter(unique_id=data)
                        temp_uuids_data.delete()

    context = {'master_form':master_form,
               'party_names':party_names,
               'items_formset':items_formset,
               'Purchase_gst':Purchase_gst,
               'godown_formsets':godown_items_formset,
               'item_godowns_raw':raw_material_godowns,
               'items':item_name_searched
               }

    return render(request,'accounts/purchase_invoice.html',context=context)


#popup page for purchase voucher godown update
def purchasevoucherpopupupdate(popup_godown_data,shade_id,prefix_id,primarykey,old_item_shade):
        
        if primarykey is not None:
            voucher_item_instance = purchase_voucher_items.objects.get(id=primarykey)

            if old_item_shade != shade_id:
                all_godown_old_instances = shade_godown_items.objects.filter(purchase_voucher_godown_item = primarykey)
                if all_godown_old_instances:
                    print('all_godown_old_instances',all_godown_old_instances)
                    for items in all_godown_old_instances:
                        items.deleted_directly = True

                        #send old shade to the signal for deleting qty from through table using temp attribute extra_data_old_shade
                        items.extra_data_old_shade = old_item_shade
                        items.delete()

            formset = purchase_voucher_items_godown_formset(popup_godown_data, instance = voucher_item_instance ,prefix='shade_godown_items_set')
            
            if formset.is_valid():
                for form in formset.deleted_forms:
                    if form.instance.pk:
                        # boolen to check if the instance was directly deleted or via models.CASCADE later used in signals
                        form.instance.deleted_directly = True
                        form.instance.delete()
                formset.save()
            else:
                print('godown_errors',formset.errors)

                


#url for this func is generated by purchasevouchercreategodownpopupurl func 
def purchasevoucherpopup(request,shade_id,prefix_id,unique_id=None,primarykey=None):
    
    #unique_id generation is on add button so created rows will not have unique id
    # create dynamic formsets depends on create or update
    
    #only for popup create and update temp table
    if unique_id is not None:
        #filter the instances by the unique_id which acts as temp primarykey for invoiceitems table
        temp_instances = shade_godown_items_temporary_table.objects.filter(unique_id=unique_id)
        
        if temp_instances:
            formsets = shade_godown_items_temporary_table_formset_update(request.POST or None, queryset = temp_instances,prefix='shade_godown_items_set')

        else:
            formsets = shade_godown_items_temporary_table_formset(request.POST or None, queryset = temp_instances,prefix='shade_godown_items_set')
    
    #only for poup get
    elif primarykey is not None:

        godowns_for_selected_shade = shade_godown_items.objects.filter(purchase_voucher_godown_item__item_shade = shade_id,purchase_voucher_godown_item = primarykey)
        
        voucher_item_instance = purchase_voucher_items.objects.get(id=primarykey)
        if godowns_for_selected_shade:
            formsets = purchase_voucher_items_godown_formset(instance = voucher_item_instance,prefix='shade_godown_items_set')
        else:
            formsets = purchase_voucher_items_godown_formset_shade_change(
            instance=voucher_item_instance,
            prefix='shade_godown_items_set',
            queryset=godowns_for_selected_shade)

    #create a formset instance with the selected unique id or PK 
    formset = formsets
    try:
        godowns = Godown_raw_material.objects.all()
        item = Item_Creation.objects.get(shades__id = shade_id) 
        item_shade = item_color_shade.objects.get(id = shade_id)

    except Exception as e:
        messages.error(request,'Error with Shades')

    if request.method == 'POST':
        formset = formsets
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    form.save()
                else:
                    context = {'godowns': godowns, 'item': item, 'item_shade': item_shade,
                                'formset': formset,'unique_id': unique_id, 'shade_id': shade_id,
                                                                 'errors': formset.errors,'prefix_id':prefix_id, 'primary_key':primarykey}
                    return render(request, 'accounts/purchase_popup.html', context)
                
            #if form is valid save the uniquekey in session for verification
            # Create temporary data and set the flag in the session to be used in purchasevouchercreateupdate  
            request.session['temp_data_exists'] = True
            temp_uuid = request.session.get('temp_uuid', [])
            temp_uuid.append(unique_id)
            request.session['temp_uuid'] = temp_uuid 

            return HttpResponse('<script>window.close();</script>') 
                    

        else:
            context = {
                'godowns': godowns, 'item': item, 'item_shade': item_shade, 'formset': formset, 
                'unique_id': unique_id, 'shade_id': shade_id, 'errors': formset.errors,'prefix_id':prefix_id, 'primary_key':primarykey
            }
            return render(request, 'accounts/purchase_popup.html', context)
    return render(request, 'accounts/purchase_popup.html' ,{'godowns':godowns,'item':item,'shade_id': shade_id,
                                                            'item_shade':item_shade,'formset':formset,
                                                            'unique_id':unique_id,'prefix_id':prefix_id, 'primary_key':primarykey})


def purchasevouchercreategodownpopupurl(request):
    shade_id = request.GET.get('selected_shade')
    unique_id = request.GET.get('unique_invoice_row_id')
    primary_key = request.GET.get('purchase_id')
    prefix_id  = request.GET.get('prefix_id')

    #if pk is there in ajax then it generates url for update if unique id is there in rquest then it generates url with unique key
    if primary_key is not None:
        popup_url = reverse('purchase-voucher-popup-update', args=[shade_id,prefix_id,primary_key])
        
    elif unique_id is not None:
        popup_url = reverse('purchase-voucher-popup-create', args=[shade_id,prefix_id,unique_id])
        
    else:
        popup_url = None

    return JsonResponse({'popup_url':popup_url})


    

def purchasevoucherlist(request):
    purchase_invoice_list = item_purchase_voucher_master.objects.all()
    return render(request,'accounts/purchase_invoice_list.html',{'purchase_invoice_list':purchase_invoice_list})


def purchasevoucherdelete(request,pk):
    purchase_invoice_pk = get_object_or_404(item_purchase_voucher_master,pk=pk)
    purchase_invoice_pk.delete()
    return redirect('purchase-voucher-list')
                    

def session_data_test(request):
    # if request.session['openingquantitytemp']:
    #     openingquantitytemp = request.session['openingquantitytemp']
    # else:
    #     openingquantitytemp == None



    # Get all data from the session
    session_data = request.session
    
    # Now session_data contains all data stored in the session
    # You can access individual items using dictionary-like syntax
    for key, value in session_data.items():
        print(f"Key: {key}, Value: {value}")

    context = {}
    return render(request,'misc/session_test.html',context=context)


#__________________________purchase voucher end__________________________



#__________________________salesvoucherstart__________________________

def salesvouchercreate(request):
    return render(request,'.html')



def salesvoucherupdate(request,pk):
    return render(request,'.html')



def salesvoucherlist(request):
    return render(request,'.html')


def salesvoucherdelete(request,pk):
    pass



#__________________________sales voucher end__________________________



#__________________________Sub Category Start___________________________



def gst_create_update(request, pk = None):
    gsts =  gst.objects.all()
    if pk:
        instance = gst.objects.get(pk=pk)
        title = 'Update'

    else:
        instance = None
        title = 'Create'


    if request.path == '/gstpopup/':
        template_name = 'accounts/gst_popup.html'
    
    elif request.path == '/gstcreate/':
        template_name = 'accounts/gst_create_update.html'


    elif request.path == f'/gstupdate/{pk}':
        template_name = 'accounts/gst_create_update.html'
 

    form = gst_form(instance = instance)
    if request.method == 'POST':
        form = gst_form(request.POST, instance = instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request,'GST updated successfully.')
            else:
                messages.success(request,'GST created successfully.')

            if 'save' in request.POST and template_name == 'accounts/gst_create_update.html':
                return redirect('gst-create-list')

            elif 'save' in request.POST and template_name == 'accounts/gst_popup.html':
                # return json of all the gst record after submit so that it will be passed to parent and updated dynamically after popup submission
                gst_updated = gst.objects.all().values('id', 'gst_percentage')
                print(list(gst_updated))
                return JsonResponse({"gst_updated": list(gst_updated)})
        else:
            print(form.errors)
            messages.success(request,'An error occured.')

    return render(request,template_name,{'form':form, 'title':title, 'gsts':gsts})






def gst_delete(request,pk):
    gst_pk = gst.objects.get(pk=pk)
    gst_pk.delete()
    messages.success(request,'GST deleted')
    return redirect('gst-create-list')



def fabric_finishes_create_update(request, pk = None):
    fabricfinishes =  FabricFinishes.objects.all()
    if pk:
        fabric_finishes_instance = FabricFinishes.objects.get(pk=pk)
        title = 'Update'
    else:
        fabric_finishes_instance = None
        title = 'Create'

    if request.path == '/fabricfinishespopup/':
        template_name = 'misc/fabric_finishes_popup.html'

    elif request.path == '/fabricfinishesscreate/' or f'/fabricfinishesupdate/{pk}':
        template_name = 'misc/fabric_finishes_create_update.html'

    form = FabricFinishes_form(instance = fabric_finishes_instance)

    if request.method == 'POST':
        form = FabricFinishes_form(request.POST,instance = fabric_finishes_instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request,'fabric finish updated sucessfully')
            else:
                messages.success(request,'fabric finish created sucessfully')

            if 'save' in request.POST and template_name == 'misc/fabric_finishes_create_update.html':
                return redirect('fabric-finishes-create-list')
            
            elif 'save' in request.POST and template_name == 'misc/fabric_finishes_popup.html':
                fabric_finishes_all = FabricFinishes.objects.all().values('id', 'fabric_finish')
                
                return JsonResponse({"fabric_finishes_all": list(fabric_finishes_all)})
        else:
            messages.error(request,'An error occured.')

    return render(request,template_name,{'form':form,'title':title,'fabricfinishes':fabricfinishes})



def fabric_finishes_delete(request,pk):
    fabric_finish =  FabricFinishes.objects.get(pk=pk)
    fabric_finish.delete()
    messages.success(request,'fabric finish deleted.')
    return redirect('fabric-finishes-create-list')


def packaging_create_update(request, pk = None):
    
    packaging_all =  packaging.objects.all()

    if pk:
        packaging_instance = packaging.objects.get(pk=pk)
        title = 'Update'
    else:
        packaging_instance = None
        title = 'Create'

    if request.path == '/packagingpop/':
        template_name = 'misc/packaging_popup.html'

    elif request.path == '/packaging_create/' or f'/packagingupdate/{pk}':
        template_name = 'misc/packaging_create_update.html'

    form = packaging_form(instance = packaging_instance)

    if request.method == 'POST':
        form = packaging_form(request.POST,instance = packaging_instance)
        if form.is_valid():
            form.save()

            if pk:
                messages.success(request,'packing updated sucessfully.')
            else:
                messages.success(request,'packing created sucessfully.')

            
            if 'save' in request.POST and template_name == 'misc/packaging_create_update.html':
                return redirect('packaging-create-list')

            elif 'save' in request.POST and template_name == 'misc/packaging_popup.html':

                packaging_all_values = packaging.objects.all().values('id','packing_material')

                return JsonResponse({'packaging_all_values': list(packaging_all_values)})
        else:
            messages.error(request, 'An error accoured.')  

    return render(request, template_name ,{'form':form,'title':title,'packaging_all':packaging_all})





def packaging_delete(request,pk):
    packaging_pk =  packaging.objects.get(pk=pk)
    packaging_pk.delete()
    messages.success(request,'Packing deleted.')
    return redirect('packaging-create-list')



#__________________________Sub Category End_____________________________



#_________________________production-start______________________________


def product2item(request,product_refrence_id):
    try:
        items = Item_Creation.objects.all().order_by('item_name')
        product_refrence_no = product_refrence_id
        Products_all = PProduct_Creation.objects.filter(Product__Product_Refrence_ID=product_refrence_id).select_related('PProduct_color')

        if not Products_all.exists():
                raise ValueError("No products found for the given reference ID.")
        
        #query for filtering unique to product fields for formset_single
        #filter all record of the products with the ref_id which is marked as unique fields
        product2item_instances = product_2_item_through_table.objects.filter(PProduct_pk__Product__Product_Refrence_ID=product_refrence_id, common_unique = False).select_related('PProduct_pk','Item_pk','PProduct_pk__PProduct_color')
        formset_single = Product2ItemFormset(queryset=product2item_instances , prefix='product2itemuniqueformset')


        # query for filtering all the common items in all the products in the refrence_id after that :
        #It orders by Item_pk first, so all records with the same Item_pk are grouped together.
        #Within each group of Item_pk, it orders by id.
        #distinct('Item_pk') will keep the first record of each group (based on the smallest id within that group).
        
        distinct_product2item_commmon_instances = product_2_item_through_table.objects.filter(PProduct_pk__Product__Product_Refrence_ID=product_refrence_id, common_unique = True).order_by('Item_pk', 'id').distinct('Item_pk').select_related('PProduct_pk','Item_pk')

        formset_common = Product2CommonItemFormSet(queryset=distinct_product2item_commmon_instances,prefix='product2itemcommonformset')
        

        if request.method == 'POST':

            formset_single = Product2ItemFormset(request.POST, queryset=product2item_instances, prefix='product2itemuniqueformset')
            formset_common = Product2CommonItemFormSet(request.POST, queryset=distinct_product2item_commmon_instances, prefix='product2itemcommonformset') 
            
            formset_single_valid = False
            formset_common_valid = False

            #for unique records
            if formset_single.is_valid():
                
                try:
                    # when using form.save(commit=False) we need to explicitly delete forms marked in has_deleted 
                    for form in formset_single.deleted_forms:
                        if form.instance.pk:  # Ensure the form instance has a primary key before attempting deletion
                            logger.info(f"Deleted product to item instace of {form.instance.pk}")
                            form.instance.delete()
                    
                    for form in formset_single:
                        if not form.cleaned_data.get('DELETE'): # check if form not in deleted forms to avoid saving it again 
                            if form.cleaned_data.get('Item_pk'):  # Check if the form has 'Item_pk' filled
                                
                                if form.instance.pk:  # This line checks if the form instance has a primary key (pk), which means it corresponds to an existing record in the database.
                                    existing_instance = product_2_item_through_table.objects.get(pk=form.instance.pk)  # fetch the existing instance from DB 
                                    initial_rows = existing_instance.no_of_rows # get the existing no of rows form DB
                                else:
                                    initial_rows = 0

                                p2i_instance = form.save(commit = False)
                                p2i_instance.common_unique = False
                                p2i_instance.row_number = form.prefix[-1]  #get the prefix no of the form
                                logger.info(f"Product to item created/updated special - {p2i_instance.id}")
                                p2i_instance.save()

                                no_of_rows_to_create = form.cleaned_data['no_of_rows'] - initial_rows   # create the rows of the diffrence 

                                if no_of_rows_to_create > 0:
                                    for row in range(no_of_rows_to_create):
                                        logger.info(f" set prod item part name created of p2i instance - {p2i_instance.id}")
                                        set_prod_item_part_name.objects.create(producttoitem = p2i_instance)

                                p2i_instance.save()
                                formset_single_valid = True
                except Exception as e:
                    logger.error(f'Error saving unique records - {e}')
                    messages.error(request, f'Error saving unique records - {e}')  
            

            #for common records
            if formset_common.is_valid():
                try:
                    for form in formset_common.deleted_forms:
                        deleted_item = form.instance.Item_pk  # get the item_pk from marked deleted forms 

                        for product in Products_all: # loop through products, filter the items with all prod from table and delete them 
                            p2i_to_delete = product_2_item_through_table.objects.filter(PProduct_pk=product, Item_pk=deleted_item, common_unique=True)
                            logger.info(f"Deleted product to item instace of {product}, - {deleted_item}")
                            p2i_to_delete.delete()
                            
                    for form in formset_common: # duplicate item for the product in the form wont give validation error as the old product will be updated instead of creating a new one and raising error of unique values  
                        if not form.cleaned_data.get('DELETE'): # check if form not in deleted forms to avoid saving it again 

                            if form.cleaned_data.get('Item_pk'):  # Check if the form has 'Item_pk' filled

                                for product in Products_all:
                                    #loop through all the products for each form and get the instance with
                                    # PProduct_pk and item_pk if exists and assign the form fields manually or create them if not created 
                                    item = form.cleaned_data['Item_pk']
                                    
                                    obj, created = product_2_item_through_table.objects.get_or_create(PProduct_pk=product, Item_pk=item, common_unique=True)
                                    
                                    # get the initial no_of_rows if new created its compared with 0 or if uts updated then obj.no_of_rows from existing  row
                                    if created:
                                        initial_rows = 0

                                    if not created:
                                        initial_rows = obj.no_of_rows

                                    obj.no_of_rows =  form.cleaned_data['no_of_rows']
                                    obj.Remark = form.cleaned_data['Remark']
                                    obj.row_number = form.prefix[-1]   #get the prefix no of the form
                                    logger.info(f"Product to item created/updated common -  {obj.id}")
                                    obj.save()


                                    # create records in set_prod_item_part_name table with the saved obj as FK 
                                    rows_to_create = form.cleaned_data['no_of_rows'] - initial_rows
                                    if rows_to_create > 0:
                                            for row in range(rows_to_create):
                                                set_prod_item_part_name.objects.create(producttoitem = obj)
                                                logger.info(f" set prod item part name created of - {obj.id}")


                                    formset_common_valid = True

                except Exception as e:
                    logger.error(f'Error saving common records - {e}')
                    messages.error(request, f'Error saving common records{e}.') 
        

            if formset_common_valid and formset_single_valid:

                messages.success(request,'Items to Product sucessfully added.')
                close_window_script = """
                                                <script>
                                                window.opener.location.reload(true);  // Reload parent window if needed
                                                window.close();  // Close current window
                                                </script>
                                                """
                return HttpResponse(close_window_script)
            
            else:
                for form_errors in formset_common.errors:
                    if form_errors:
                        logger.error(f'Error with formset_common form - {product_refrence_id } - {form_errors}')
                        messages.error(request, f'{form_errors}')

                for form_errors in formset_single.errors:
                    if form_errors:
                        logger.error(f'Error with formset_common form - {product_refrence_id } - {form_errors}')
                        messages.error(request, f'{form_errors}')


                close_window_script = """
                            <script>
                                                window.opener.location.reload(true);  // Reload parent window if needed
                                                window.close();  // Close current window
                                                </script>
                                                """
                return HttpResponse(close_window_script)


        return render(request,'production/product2itemsetproduction.html', { 'formset_single':formset_single,'formset_common':formset_common,
                                                                'Products_all':Products_all,
                                                                'items':items,'product_refrence_no': product_refrence_no})

    except Exception as e:
        logger.error(f'Error with forms - {product_refrence_id } - {e}')
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return render(request, 'production/product2itemsetproduction.html', {
            'formset_single': formset_single,
            'formset_common': formset_common,
            'Products_all': Products_all,
            'items': items,
            'product_refrence_no': product_refrence_no
        })




def export_Product2Item_excel(request,product_ref_id):
    
    try:
        # for refrence ORM_query_dump
        products_in_i2p_special = product_2_item_through_table.objects.filter(
            PProduct_pk__Product__Product_Refrence_ID=product_ref_id,common_unique = False).order_by(
            'row_number')
    
        products_in_i2p_common = product_2_item_through_table.objects.filter(
            PProduct_pk__Product__Product_Refrence_ID=product_ref_id,common_unique = True).order_by(
            'Item_pk', 'id').distinct('Item_pk')

        
        if not products_in_i2p_special and not products_in_i2p_common:
            logger.error(f"Add Items to the respective Products first - {product_ref_id}")
            raise ObjectDoesNotExist("Add Items to the respective Products first")

        wb = Workbook()

        ##delete the default workbook
        default_sheet = wb['Sheet']
        wb.remove(default_sheet)    

        wb.create_sheet('product_special_configs')
        wb.create_sheet('product_common_configs')

        sheet1 = wb.worksheets[0]
        sheet2 = wb.worksheets[1]


        
        column_widths = [10, 40, 20, 30, 20, 15, 10, 10]  # Adjust these values as needed

        #fix the column width  of sheet1
        for i, column_width in enumerate(column_widths, start=1):  # enumarate is used to get the index no with the value on that index
            col_letter = get_column_letter(i)
            sheet1.column_dimensions[col_letter].width = column_width


        #fix the column width  of sheet2
        for i, column_width in enumerate(column_widths, start=1):
            col_letter = get_column_letter(i)
            sheet2.column_dimensions[col_letter].width = column_width



        #for product_special_configs
        headers =  ['id','item name', 'product sku','part name', 'part dimention','dimention total','part pieces','grand_total']
        sheet1.append(headers)

        row_count_to_unlock_total = 1
        for product in products_in_i2p_special:
            grand_total_parent = product.grand_total

            rows_to_insert_s1 = []
            for product_configs in product.product_item_configs.all():
                rows_to_insert_s1.append([
                product_configs.id,
                product_configs.producttoitem.Item_pk.item_name,
                product_configs.producttoitem.PProduct_pk.PProduct_SKU,
                product_configs.part_name,
                product_configs.part_dimentions,
                product_configs.dimention_total,
                product_configs.part_pieces
            
            ])
            
            row_count_to_unlock = 1

            for row in rows_to_insert_s1:
                sheet1.append(row)
                row_count_to_unlock = row_count_to_unlock + 1

            row_count_to_unlock_total =  row_count_to_unlock_total + row_count_to_unlock


            # Insert a blank row and grand total from parent model in sheet after every product data has inserted
            sheet1.append(['','','','','','','', grand_total_parent])
        
            rows_to_insert_s1.clear()

        # unlock the rows ment for editing 
        for row in sheet1.iter_rows(min_row=2, max_row=row_count_to_unlock_total, min_col=4, max_col=7):
            for cell in row:
                cell.protection = Protection(locked = False)



        # for product_common_configs
        headers =  ['id','item name','part name', 'part dimention','dimention total','part pieces', 'g total']
        sheet2.append(headers)


        row_count_to_unlock_total_common = 1
        for product in products_in_i2p_common:
            grand_total_parent = product.grand_total

            rows_to_insert_s2 = []
            for product_configs in product.product_item_configs.all():
                rows_to_insert_s2.append([
                product_configs.id,
                product_configs.producttoitem.Item_pk.item_name,
                product_configs.part_name,
                product_configs.part_dimentions,
                product_configs.dimention_total,
                product_configs.part_pieces
            ])

            row_count_to_unlock = 1

            for row in rows_to_insert_s2:
                sheet2.append(row)
                row_count_to_unlock = row_count_to_unlock + 1
            row_count_to_unlock_total_common =  row_count_to_unlock_total_common + row_count_to_unlock


            # Insert a blank row and grant total from parent in sheet after every product data has inserted
            sheet2.append(['','','','','','', grand_total_parent])

            rows_to_insert_s2.clear()

        # unlock the rows ment for editing 
        for row in sheet2.iter_rows(min_row=2, max_row=row_count_to_unlock_total_common, min_col=3, max_col=7):
            for cell in row:
                cell.protection = Protection(locked = False)



        # Protect the entire worksheet
        sheet1.protection.sheet = True
        sheet2.protection.sheet = True

        fileoutput = BytesIO()
        wb.save(fileoutput)
        
        # Prepare the HTTP response with the Excel file content
        response = HttpResponse(fileoutput.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file_name_with_pk = f'product_reference_id_{product_ref_id}'
        response['Content-Disposition'] = f'attachment; filename="{file_name_with_pk}.xlsx"'

        return response
    
    except product_2_item_through_table.DoesNotExist:
        messages.error(request, 'No data found for the given product reference ID.')
        logger.error(f"items for product Does not exists for refrence id {product_ref_id}")
        return redirect(reverse('edit_production_product', args=[product_ref_id]))
    
    except Exception as e:
        messages.error(request, f'An error occurred while exporting data {e}')
        logger.error(f"An exception occoured while exporting data - {e} for ref id {product_ref_id}")
        return redirect(reverse('edit_production_product', args=[product_ref_id]))


# view configs of single products
def viewproduct2items_configs(request,product_sku):
    product2item_instances = product_2_item_through_table.objects.filter(PProduct_pk__PProduct_SKU=product_sku)

    product2item_instances_first = product_2_item_through_table.objects.filter(PProduct_pk__PProduct_SKU=product_sku).first()

    return render(request,'production/product2itemsconfigview.html',{'product2item_instances' : product2item_instances,
                                                                     "product2item_instances_first":product2item_instances_first})
    


def purchaseorderrawcreateupdate(request,pk= None):

    print(request.POST)
    if pk:
        instance = get_object_or_404(purchase_order, pk = pk)

    else:
        instance = None

    ledger_party_names = Ledger.objects.filter(under_group__account_sub_group = 'Sundray Debtor(we sell)')
    
    products = Product.objects.all()

    form = purchase_order_form(instance=instance)
    
    if request.method == 'POST':
        form = purchase_order_form(request.POST, instance=instance)

        if form.is_valid():
            print(form.cleaned_data['target_date'])
            form.save()
            return redirect('purchase-order-raw-list')
    

    return render(request,'production/purchaseorderrawcreateupdate.html',{'form':form ,
                                                                          'ledger_party_names':ledger_party_names,
                                                                          "products":products})



def purchaseorderrawlist(request):

    purchase_orders = purchase_order.objects.all()

    return render(request,'production/purchaseorderrawlist.html',{'purchase_orders':purchase_orders})



def purchaseorderrawdelete(request,pk):
     
    try:
        instance = get_object_or_404(purchase_order, pk = pk)
        instance.delete()
        logger.info(f"Purchase Order with order no - {instance.purchase_order_number} was deleted")
        messages.success(request,f'Purchase Order with order no - {instance.purchase_order_number} was deleted')
        
    
    except exception as e:
        messages.error(request,f'Cannot delete {instance.purchase_order_number} - {e}.')
        logger.error(f"Cannot delete {instance.purchase_order_number} - {e}.")
    return redirect('purchase-order-raw-list')
     

#_________________________production-end______________________________


#__________________________common-functions-start____________________________


def itemdynamicsearchajax(request):
    try:
        # Retrieve the partial name typed by the user from the GET request
        item_name_typed = request.GET.get('nameValue')

        if not item_name_typed:
            raise ValidationError("partial name provided.")
        logger.info(f"searched keyword via itemdynamicsearchajax {item_name_typed}")
        
        item_name_searched = Item_Creation.objects.filter(item_name__icontains=item_name_typed)

        if item_name_searched:
            # Prepare a dictionary of searched items with IDs as keys and names as values
            searched_item_name_dict = {queryset.id: queryset.item_name for queryset in item_name_searched}
            logger.info(f"searched result via itemdynamicsearchajax {searched_item_name_dict}")
            """
            or 
            searched_item_name_dict = {}
            for queryset in item_name_searched:
                item_name = queryset.item_name
                item_id = queryset.id
                searched_item_name_dict[item_id] = item_name
            """

            return JsonResponse({'item_name_typed': item_name_typed, 'searched_item_name_dict': searched_item_name_dict}, status=200)
        else:
            return JsonResponse({'error': 'No items found.'}, status=404)

    except ValidationError as ve:
        error_message = str(ve)
        logger.error(f"Validaton errorin itemdynamicsearchajax - {ve}")
        return JsonResponse({'error': error_message}, status=400)
    
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return JsonResponse({'error': error_message}, status=500)



#__________________________reports-start-end_________________________________

def creditdebitreport(request):
    all_reports = account_credit_debit_master_table.objects.all()

    return render(request,'misc/purchase_report.html',{'all_reports':all_reports})

#__________________________reports-end____________________________________



#_______________________authentication View start___________________________
def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(request, username=username,password=password)
            if user is not None:
                auth.login(request,user)
                
                return redirect('index')
    context = {'form':form}
    return render(request, 'misc/login.html', context=context)



def register(request):
    form = CreateUserForm(request.POST) # this will be shown as a blank form to user before the post request 
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            print('Name:',form.cleaned_data['username']) #validated data stored in cleaned_data attribute
            print('Name:',form.cleaned_data['password1'])
            user = form.save()
            group = Group.objects.get(name='Worker') #add in grp while register
            user.groups.add(group) #add in grp while register
            
            return redirect('login')

    context = {'form':form}
    return render(request, 'product/register.html',context=context)


#_______________________authentication View end___________________________





#_________________________________________ Cosmus ERP Code_______________________




# def add_product(request):
#     form = ProductForm()
#     if request.method == 'POST':
#         form = ProductForm(request.POST,request.FILES) 
#         print(request.POST)
#         print(request.FILES)
#         if form.is_valid():
#             # product = Product(
#             #     # reference_image=request.FILES.get('reference_image'),
#             #     Product_Name=form.cleaned_data['Product_Name'],
#             #     Model_Name=form.cleaned_data['Model_Name'],
#             #     Product_Status=form.cleaned_data['Product_Status'],
#             #     Product_Channel = form.cleaned_data['Product_Channel'],
#             #     Product_SKU = form.cleaned_data['Product_SKU'],
#             #     Product_HSNCode =  form.cleaned_data['Product_HSNCode'],
#             #     Product_WarrantyTime = form.cleaned_data['Product_WarrantyTime'],
#             #     Product_MRP =  form.cleaned_data['Product_MRP'],
#             #     Product_SalePrice_CustomerPrice =  form.cleaned_data['Product_SalePrice_CustomerPrice'],
#             #     Product_BulkPrice = form.cleaned_data['Product_BulkPrice'],
#             #     Product_Cost_price = form.cleaned_data['Product_Cost_price']
#             #)
#             # product.save()
#             #or
#             product = form.save(commit=False)
#             product.images = ProductImage.objects.create(Image=request.FILES['Image'])
#             form.save()
#             return redirect('listproduct')

#     else:
#         return render(request, 'product/add_product.html', {'form':form})
#     return render(request, 'product/add_product.html',{'form': form})



# def edit_product(request, pk):
#     product = Product.objects.get(id = pk)
#     form = EditProductForm(instance=product)

#     if request.method == "POST":
#         form = EditProductForm(request.POST, instance=product) # request.POST has the data from the form and instance has the data from the database
#         if form.is_valid():
#             form.save() # saves the product changes in the database

#             # handles images
#             #request.POST has data sent by the form in key value pair 
#             #where key corresponds to the name = field in the form and value is the actual data
#             for i in range(1,11): # as we have 10 images to upload
#                 image_type = request.POST.get(f'Image_type_{i}')
#                 order_by =  request.POST.get(f'Order_by_{i}')
#                 image_file = request.FILES.get(f'Image_{i}')  
#                 #Product=product (product = Product.objects.get(id = pk)), Image_ID=i,: These are the conditions for
#                 #finding an existing ProductImage instance. It looks for an instance where the 
#                 #associated product is the given product and the Image_ID is equal to i. 
#                 #defaults={'Image': image_file, 'Image_type': image_type, 'Order_by': order_by}: 
#                 #If no matching instance is found, this dictionary specifies the default values 
#                 #to use when creating a new instance. It sets the image file (Image), image type 
#                 #(Image_type), and order (Order_by) with the values obtained from the form.
                
#                 if image_file:
#                     #ProductImage.objects.get_or_create(: This is a manager method 
#                     #(objects is the default manager for a Django model) that interacts with the database.
#                     #Get or create an image 
#                     product_image, created = ProductImage.objects.get_or_create(
#                         Product = product, Image_ID = i,
#                         defaults = {'Image':image_file, 'Image_type':image_type, 'Order_by': order_by}
#                     )

#                     if not created:
#                         #update the existing product
#                         product_image.Image = image_file
#                         product_image.Image_type = image_type
#                         product_image.Order_by = order_by
#                         product_image.save()
#             return redirect('listproduct')
#     context = {'form': form, 'product': product}
#     return render(request, 'product/edit_product.html', context)
