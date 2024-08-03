import decimal
from email import message
from io import BytesIO
from itertools import count
from operator import is_
from sys import exception
from django.conf import settings
from django.contrib.auth.models import User , Group
from django.core.exceptions import ValidationError , ObjectDoesNotExist
import json
from pandas import json_normalize
from python_utils import raise_exception
import requests
from django.contrib.auth.models import auth 
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Sum, ProtectedError, Avg, Count,F
from django.db.models.functions import Round
from django.db import DatabaseError, IntegrityError, transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
import logging
import urllib.parse
from django.contrib import messages
from openpyxl.utils import get_column_letter 
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Protection
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import inlineformset_factory, modelformset_factory
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseServerError, JsonResponse, QueryDict

from django.db.models import OuterRef, Subquery, DecimalField, F
from django.db.models.functions import Coalesce

from . models import (AccountGroup, AccountSubGroup, Color, Fabric_Group_Model,
                       FabricFinishes, Godown_finished_goods, Godown_raw_material,
                         Item_Creation, Ledger, MainCategory, PProduct_Creation, Product,
                           Product2SubCategory,  ProductImage, RawStockTransferMaster, StockItem,
                             SubCategory, Unit_Name_Create, account_credit_debit_master_table, cutting_room,  factory_employee,
                               gst, item_color_shade, item_godown_quantity_through_table,
                                 item_purchase_voucher_master, labour_workout_cutting_items, labour_workout_master, opening_shade_godown_quantity, 
                                 packaging, product_2_item_through_table, product_to_item_labour_workout, purchase_order, 
                                 purchase_order_for_raw_material, purchase_order_raw_material_cutting, 
                                 purchase_order_to_product, purchase_order_to_product_cutting, purchase_voucher_items,
                                   set_prod_item_part_name, shade_godown_items,
                                   shade_godown_items_temporary_table,purchase_order_for_raw_material_cutting_items)

from .forms import(Basepurchase_order_for_raw_material_cutting_items_form, ColorForm, 
                   CreateUserForm, CustomPProductaddFormSet, ProductCreateSkuFormsetCreate,
                     ProductCreateSkuFormsetUpdate, UserRoleForm,  cutting_room_form,
                       factory_employee_form, labour_workout_cutting_items_form, labour_workout_master_form, purchase_order_for_raw_material_cutting_items_form, 
                       purchase_order_to_product_cutting_form,raw_material_stock_trasfer_items_formset,
                    FabricFinishes_form, ItemFabricGroup, Itemform, LedgerForm,
                     OpeningShadeFormSetupdate, PProductAddForm, PProductCreateForm, ShadeFormSet,
                       StockItemForm, UnitName, account_sub_grp_form, PProductaddFormSet,
                        ProductImagesFormSet, ProductVideoFormSet, purchase_order_form,purchase_voucher_items_godown_formset_shade_change,
                         gst_form, item_purchase_voucher_master_form,
                           packaging_form, product_main_category_form, 
                            product_sub_category_form, purchase_voucher_items_formset,
                             purchase_voucher_items_godown_formset, purchase_voucher_items_formset_update, raw_material_stock_trasfer_master_form,
                                shade_godown_items_temporary_table_formset,shade_godown_items_temporary_table_formset_update,
                                Product2ItemFormset,Product2CommonItemFormSet,purchase_order_product_qty_formset,
                                purchase_order_raw_product_qty_formset,purchase_order_raw_product_qty_cutting_formset,
                                purchase_order_cutting_approval_formset,labour_workout_product_to_items_formset,
                                purchase_order_raw_product_sheet_form,purchase_order_raw_material_cutting_form)


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

@login_required(login_url='login')
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
            print(form.errors)
            print(formset.errors)
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




# def product_color_sku(request,ref_id = None):
#     color = Color.objects.all()

#     try:
#         if request.method == 'POST':
#             product_ref_id = request.POST.get('Product_Refrence_ID')
#             request_dict = request.POST
#             count = 0

#             for x in request_dict.keys():
#                 if x[0:12] == 'PProduct_SKU':
#                     count = count + 1

#             with transaction.atomic():
#                 all_sets_valid = False

#                 try:
#                     for i in range(1, count): 
#                         # Build field names dynamically 
#                         image_field_name = f'PProduct_image_{i}'
#                         color_field_name = f'PProduct_color_{i}'
#                         sku_field_name = f'PProduct_SKU_{i}'
#                         Ean_field_name = f'Product_EANCode_{i}'


#                         # Create a dictionary with the dynamic field names
#                         data = {
#                             'PProduct_color': request.POST.get(color_field_name),
#                             'PProduct_SKU': request.POST.get(sku_field_name),
#                             'Product_EANCode': request.POST.get(Ean_field_name),
#                             'Product_Refrence_ID': product_ref_id
#                         }
#                         files = {
#                             'PProduct_image': request.FILES.get(image_field_name)
#                         }
                
#                         current_form = PProductCreateForm(data, files)

#                         if current_form.is_valid():
#                             pproduct = current_form.save(commit=False)
#                             # Create a new Product instance or get an existing one based on Product_Refrence_ID
#                             # product will be the object retrieved from the db and then created ,created will be a boolean field
#                             product, created = Product.objects.get_or_create(Product_Refrence_ID=product_ref_id)
#                             #product = Product.objects.create(Product_Refrence_ID=product_ref_id)
                    
#                             # Associate the PProduct instance with the Product
#                             pproduct.Product = product

#                             #The variable pproduct holds the unsaved instance of the PProduct_Creation model. 
#                             #This instance is populated with the data from the form, and you can use it to perform 
#                             #any additional logic or modifications before finally saving it to the database.
#                             pproduct.save()
#                             all_sets_valid = True

#                         else:
#                             all_sets_valid = False
#                             #explicitly set transaction to rollback on errors
#                             transaction.set_rollback(True)
#                             break

#                 except Exception as e:
#                     print('Exception occured:', str(e))
#                     messages.error(request, f'Exception occured - {e}')


#             if all_sets_valid:
#                 messages.success(request, f'Products for Refrence ID {product_ref_id} created')
#                 # reverse is used to generate a url with both the arguments, which then redirect can use to redirect
#                 return redirect(reverse('edit_production_product', args=[product_ref_id]))
            
#             else:

#                 #Return a response with errors for invalid sets of fields
#                 return render(request, 'product/product_color_sku.html', {'form':current_form,'color': color})
#     except Exception as e:
#         print('Exception occured', str(e))
#         messages.error(request,'Add a product first for Reference ID')
        
    
#     form = PProductCreateForm()
#     return render(request, 'product/product_color_sku.html', {'form': form, 'color': color,'ref_id': ref_id})


def product_color_sku(request,ref_id = None):

    color = Color.objects.all()

    if ref_id:
        instance = get_object_or_404(Product, Product_Refrence_ID=ref_id) 
        formset = ProductCreateSkuFormsetUpdate(request.POST or None,request.FILES or None, instance=instance)

    else:
        instance = None
        formset = ProductCreateSkuFormsetCreate(request.POST or None,request.FILES or None, instance=instance)

    

    if request.method == 'POST':
        product_ref_id = request.POST.get('Product_Refrence_ID', None)
        
        # only changed forms for validation are allowed
        formset.forms = [form for form in formset if form.has_changed()]

        if product_ref_id:
            if formset.is_valid():
                try:
                    for form in formset:
                        if form.is_valid():
                            form_instance = form.save(commit=False)  # save the form with commit = false
                            obj, created =  Product.objects.get_or_create(Product_Refrence_ID=product_ref_id) # create a parent instance with the entered refrence id or get the instance if already created 
                            form_instance.Product = obj   #assign the parent instance to childs FK field 
                            form_instance.save() # save the form

                    return redirect(reverse('edit_production_product', args=[product_ref_id]))
                        
                except ValidationError as ve :
                    messages.error(request,f'{ve}')
                    logger.error(ve)

                except Exception as e :
                    messages.error(request,f'{e}')
                    logger.error(e)
            else:
                return render(request, 'product/product_color_sku.html', {'formset': formset, 'color': color,'ref_id': ref_id})


    return render(request, 'product/product_color_sku.html', {'formset': formset, 'color': color,'ref_id': ref_id})




def pproduct_list(request):
    
    queryset = Product.objects.all().order_by('Product_Name').select_related('Product_GST').prefetch_related('productdetails','productdetails__PProduct_color')

    product_search = request.GET.get('product_search','')
    
    if product_search != '':
        queryset = Product.objects.filter(Q(Product_Name__icontains=product_search)|
                                            Q(Model_Name__icontains=product_search)|
                                            Q(Product_Refrence_ID__icontains=product_search)|
                                            Q(productdetails__PProduct_SKU__icontains=product_search)).distinct()
    print(queryset)
    # Number of items per page
    paginator = Paginator(queryset, 3)  # Show 10 products per page
    
    # Get the current page number from the request
    page_number = request.GET.get('page')
    
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g. 9999), deliver the last page of results
        products = paginator.page(paginator.num_pages)

    # Custom pagination range logic
    index = products.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 2 if index >= 2 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'products': products,
        'page_range': page_range,
        'product_search':product_search
    }

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
    print(request.POST)
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

    queryset = MainCategory.objects.all()

    main_cat_product_search = request.GET.get('main_cat_product_search','')

    if main_cat_product_search != '':
        queryset = MainCategory.objects.filter(product_category_name__icontains = main_cat_product_search)



    if pk:
        instance = MainCategory.objects.get(pk=pk)
        title = 'Update'
        message = 'updated'
    else:
        instance = None
        title = 'Create'
        message = 'created'

    
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
        else:
            return render(request,'product/definemaincategoryproduct.html',{'form':form,'main_cats':queryset,
                                                                    'title':title,'main_cat_product_search':main_cat_product_search})
        
    return render(request,'product/definemaincategoryproduct.html',{'form':form,'main_cats':queryset,
                                                                    'title':title,'main_cat_product_search':main_cat_product_search})


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
    
    g_search = request.GET.get('item_search','')


    #select related for loading forward FK relationships and prefetch related for reverse relationship  
    #annotate to make a temp column in item_creation for the sum of all item and its related shades in all godowns 
    queryset = Item_Creation.objects.all().annotate(total_quantity=Sum('shades__godown_shades__quantity')).order_by('item_name').select_related('Item_Color','unit_name_item',
                                                    'Fabric_Group','Item_Creation_GST','Item_Fabric_Finishes',
                                                    'Item_Packing').prefetch_related('shades',
                                                    'shades__godown_shades')


    # cannot use icontains on foreignkey fields even if it has data in the fields
    if g_search != '':
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

    return render(request,'product/list_item.html', {"items":queryset,"item_search":g_search})
    


def item_edit(request,pk): 
    
    title = 'Item update'
    gsts = gst.objects.all()
    fab_grp = Fabric_Group_Model.objects.all()
    unit_name = Unit_Name_Create.objects.all()
    colors = Color.objects.all()
    packaging_material_all = packaging.objects.all()
    fab_finishes = FabricFinishes.objects.all()
    item_pk = get_object_or_404(Item_Creation ,pk = pk)

    form = Itemform(instance=item_pk)

    # setting filtered queryset with annototed column of total_quantity  and total_rate to the formset 
    queryset = item_color_shade.objects.filter(items = pk).annotate(total_quantity=Sum('godown_shades__quantity'),
                                                                     total_value=Sum(F('godown_shades__quantity') * F('godown_shades__item_rate'), 
                                                                                output_field=DecimalField(max_digits=10, decimal_places=2)))
    for x in queryset:
        print(x.total_quantity)
        print(x.total_value)
    formset = ShadeFormSet(instance= item_pk, queryset=queryset)

    # when in item_edit the item is edited u can also edit or add shades to it which also gets updated or added
    # as item_edit instance is also provided while updating or adding with formsets to the shades module
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES , instance = item_pk)
        formset = ShadeFormSet(request.POST , request.FILES, instance = item_pk)
        formset.forms = [form for form in formset if form.has_changed()] # check for changed forms in shadeformset
        try:
            if form.is_valid() and formset.is_valid():
                form.save()  # save the item form

                for form in formset.deleted_forms: # delete forms marked for deleting in shade formset
                    if form.instance.pk:
                        form.instance.delete()

                for form in formset: #shade form
                    if form.is_valid():

                        if form.instance.pk: # if form has already created save it 
                            form.save()

                        else:  # if form is not already created then save the form and create forms of opening godown from request.POST and save them with the form instance
                            # to check if form dosen't have delete in it as it will get saved again if deleted from above code 
                            if not form.cleaned_data.get('DELETE'):
                                shade_form_instance = form.save(commit=False) # save the form with commit = False
                                shade_form_instance.save() # save the form

                                form_prefix_number = form.prefix[-1] # gives the prefix number of the current iteration of the form
                                opening_godown_quantity = request.POST.get(f'shades-{form_prefix_number}-openingValue') # get the opening godown data of the form instance from POST request 

                                if opening_godown_quantity != '':
                                    opening_godown_quantity_dict = json.loads(opening_godown_quantity)
                                    opening_godown_qty_data = opening_godown_quantity_dict.get('newData')
                                    
                                    # create forms with data from post of opening godown form
                                    item_godown_formset_data = {}
                                    for key , value in opening_godown_qty_data.items():
                                        form_set_id = key.split('_')[-1]

                                        new_data_get = opening_godown_qty_data.get(key)
                                        
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-TOTAL_FORMS'] = str(len(opening_godown_qty_data))
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-INITIAL_FORMS'] =  str(0)
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-MIN_NUM_FORMS'] =  str(0)
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-MAX_NUM_FORMS'] =  str(1000)
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_godown_id'] = new_data_get.get('godownData')
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_quantity'] = new_data_get.get('qtyData')
                                        item_godown_formset_data[f'opening_shade_godown_quantity_set-{form_set_id}-opening_rate'] = new_data_get.get('rateData')
                                    
                                    #formset for saving opening godown data  from request.post
                                    new_godown_opening_formsets = OpeningShadeFormSetupdate(item_godown_formset_data, prefix='opening_shade_godown_quantity_set')

                                    for form in new_godown_opening_formsets:
                                        if form.is_valid():
                                            form_instance = form.save(commit = False)
                                            form_instance.opening_purchase_voucher_godown_item = shade_form_instance
                                            form_instance.save()
                                    
                messages.success(request,'Item updated successfully')
                return redirect('item-list')
            
        except ProtectedError as e:
            # Handle the specific ProtectedError exception
            messages.error(request,f"Cannot delete item_color_shade due to protected foreign keys: {e}")
            logger.error(f"Cannot delete item_color_shade due to protected foreign keys: {e}")
            print(f"Cannot delete item_color_shade due to protected foreign keys: {e}")

        except exception as e:
             logger.error(f'An exception occured in item edit - {e}')
             return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
                                                                 'packaging_material_all':packaging_material_all,
                                                                 'fab_finishes':fab_finishes,
                                                                 'form':form,
                                                                 'formset': formset})
        
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
    
    godowns =  Godown_raw_material.objects.all()

    formset = None
    shade_instance = None
    try:
        # if shade form is already created
        if parent_row_id is not None and primary_key is not None:
            shade_instance = get_object_or_404(item_color_shade,pk=primary_key)
            formset = OpeningShadeFormSetupdate(request.POST or None, instance = shade_instance, prefix = "opening_shade_godown_quantity_set")
            
        # if shade form is not created and opening godown is also not created 
        elif primary_key is None and parent_row_id is not None:

            decoded_data = False
            encoded_data = request.GET.get('data')
            
            # if data in url get the data saved in url params 
            if encoded_data:
                decoded_data = json.loads(urllib.parse.unquote(encoded_data))
                new_row_data = decoded_data.get('newData', {})
                initial_data_backend = []
                
                
                for key, value in new_row_data.items():
                    initial_data_backend.append({
                            "opening_godown_id": int(value['godownData']),
                            "opening_quantity": float(value['qtyData']),
                            "opening_rate": float(value['rateData'])})

                
                # create form with that data with initial data 
                total_forms = len(initial_data_backend)
                opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_godown_id','opening_quantity','opening_rate'], extra=total_forms, can_delete=True)   # when using modelformset need to add can_delete = True or delete wont be added in the form
                formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),initial=initial_data_backend, prefix = "opening_shade_godown_quantity_set")
                
            else:
                # if no data in url create an empty form
                opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_rate','opening_quantity','opening_godown_id'], extra=1, can_delete=True)            
                formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),prefix = "opening_shade_godown_quantity_set")
        
        if request.method == 'POST':
            # save the data only if shade instance is already created, if its not created then the data is sent to parent 
            # in json format for rendering it again if required as initial data or saving it with the parent(item_edit) form submission with the shade instance
            if primary_key is not None:

                for form in formset.deleted_forms: # delete forms marked for deleting in shade formset
                    if form.instance.pk:
                        try:
                            form.instance.delete()
                        except Exception as e:

                            return JsonResponse({"error": str(e)}, status=400)

                formset.forms = [form for form in formset if form.has_changed()] # has_changed() It will return True if any form in the formset has changed, otherwise, it returns False.
                if formset.is_valid():
                    for form in formset:
                        if form.is_valid():
                            if not form.cleaned_data.get('DELETE'):
                                try:
                                    old_opening_instance = opening_shade_godown_quantity.objects.get(id= form.instance.id) # old quantity for signal purpose
                                    
                                    form_instance = form.save(commit=False)

                                    form_instance.old_opening_godown_id = old_opening_instance.opening_godown_id # old godown id to check if godown has changed or not for signal
                                    form_instance.old_opening_g_quantity = old_opening_instance.opening_quantity # old quantity for signal purpose 
                                    form_instance.save()

                                except opening_shade_godown_quantity.DoesNotExist:
                                    form_instance = form.save(commit=False)
                                    # set the old opening quantity to 0 if instance is not there (which can be the case if shade is created but godown opening instances are not) old godown_id not reqired in new created instances
                                    form_instance.old_opening_g_quantity = 0 
                                    form_instance.save()
                                
                                except Exception as e:
                                    # Handle other exceptions
                                    return JsonResponse({"error": str(e)}, status=400)

                    return HttpResponse('<script>window.close();</script>') 
                
                else:
                    logging.error(f'Error in item opening godown formset{formset.error})')
                    return JsonResponse({"errors": formset.errors}, status=400)
                
    except exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)     
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
    # except IntegrityError as e:
    #     messages.error(request, f'Cannot delete {item_pk.item_name} because it is referenced by other objects.')
    except Exception as e:
         messages.error(request, f'EXCEPTION-{e}')
         print(e)
    return redirect('item-list')




#_____________________Item-Views-end_______________________

#_____________________Color-start________________________



def color_create_update(request, pk=None):

    queryset = Color.objects.all()
    color_search = request.GET.get('color_search','')

    if color_search != '':
        queryset = Color.objects.filter(color_name__icontains = color_search)



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
            return render(request, template_name, {'title': title,'form': form,'colors':queryset,'color_search':color_search})

    return render(request, template_name , {'title': title, 'form': form, 'colors':queryset,'color_search':color_search})
        

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
    queryset = Fabric_Group_Model.objects.all()

    fabric_group_search = request.GET.get('fabric_group_search','')

    if fabric_group_search != '':
        queryset = Fabric_Group_Model.objects.filter(fab_grp_name__icontains = fabric_group_search)

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
            return render(request,template_name,{'title': title,"fab_group_all":queryset,"fabric_group_search":fabric_group_search,
                                                                                  'form':form})


    return render(request,template_name,{'title': title, "fab_group_all":queryset,"fabric_group_search":fabric_group_search,
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
    
    queryset = Unit_Name_Create.objects.all()

    unit_name_search =  request.GET.get('unit_name_search','')

    if unit_name_search != '':
        queryset = Unit_Name_Create.objects.filter(unit_name__icontains = unit_name_search)


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
            return render(request, template_name, {'title': title,'form':form,"unit_name_all":queryset,'unit_name_search':unit_name_search})
        
    else:
        return render(request, template_name, {'title':title,'form':form,"unit_name_all":queryset,'unit_name_search':unit_name_search})





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

def account_sub_group_create_update(request, pk=None):
    print(request.POST)

    groups = AccountSubGroup.objects.select_related('acc_grp').all()

    if pk:
        instance = get_object_or_404(AccountSubGroup ,pk=pk)
        title = 'Update'
    else:
        instance = None
        title = 'Create'

    main_grp = AccountGroup.objects.all()
    form = account_sub_grp_form(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Account sub-group created sucessfully')
            return redirect('account_sub_group-create')
        else:
            return render(request,'product/acc_sub_grp_create_update.html', {'main_grp':main_grp,
                                                                             'title':title,
                                                                             'form':form, "groups":groups})

    return render(request,'product/acc_sub_grp_create_update.html', {'main_grp':main_grp, 
                                                                     'title':title,
                                                                     'form':form, "groups":groups})



def account_sub_group_delete(request, pk):  
    try:
        group = get_object_or_404(AccountSubGroup ,pk=pk)
        group.delete()
        messages.success(request,f'Account Sub Group {group.account_sub_group} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {group.account_sub_group} because it is referenced by other objects.')
    return redirect('account_sub_group-create')



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

            elif debit_credit_value == 'N/A':
                account_credit_debit_master_table.objects.create(ledger = ledger_instance, voucher_type = 'Ledger',credit= 0, debit= 0)

            messages.success(request,'Ledger Created')
            return redirect('ledger-list')
        
        else:

            return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create'})
    
    return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create'})
    

@transaction.atomic
def ledgerupdate(request,pk):
    under_groups = AccountSubGroup.objects.all()
    
    Ledger_pk = get_object_or_404(Ledger,pk = pk)
    ledgers = Ledger_pk.transaction_entry.all() #get all credit_debit model transactions related instances to the ledger

    Opening_ledger = ledgers.filter(voucher_type ='Ledger').first() # filter the first related instance for only ledger as voucher type
    form = LedgerForm(instance = Ledger_pk)
    opening_balance = 0

    if form.instance.Debit_Credit == 'Debit':            # if form instance has Debit 
        opening_bal = Opening_ledger.debit               # get the data from the debit side of transaction_entry
        opening_balance = opening_balance + opening_bal  # and store it in opening_balance variable

    elif form.instance.Debit_Credit == 'Credit':         # if form instance has Credit
        opening_bal = Opening_ledger.credit              # get the data from the credit side of transaction_entry
        opening_balance = opening_balance + opening_bal  # and store it in opening_balance variable

    elif form.instance.Debit_Credit == 'N/A': # if form instance has N/A 
        opening_balance = opening_balance # opening_balance will be 0 

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

            if request.POST['Debit_Credit'] == 'N/A':
                Opening_ledger.credit = 0
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
            try:
                godown_raw = Godown_raw_material(godown_name_raw=godown_name) #instance of Godown_raw_material
                godown_raw.save()  #save the instance to db 
                messages.success(request,'Raw material godown created.')

                if 'save' in request.POST:
                    return redirect('godown-list')
                elif 'save_and_add_another' in request.POST:
                    return redirect('godown-create')
                
            except ValidationError as ve:
                messages.error(request,f"{ve}")
                return redirect('godown-list')

            except Exception as e:
                messages.error(request,f"{e}")
                return redirect('godown-list')
        
        elif godown_type == 'Finished Goods':
            try:
                godown_finished = Godown_finished_goods(godown_name_finished=godown_name) #instance of Godown_finished_goods
                godown_finished.save() #save the instance to db 
                messages.success(request,'Finished goods godown created.')

                if 'save' in request.POST:
                    return redirect('godown-list')
                elif 'save_and_add_another' in request.POST:
                    return redirect('godown-create')
            
            except ValidationError as ve:
                messages.error(request,f"{ve}")
                return redirect('godown-list')

            except Exception as e:
                messages.error(request,f"{e}")
                return redirect('godown-list')
            
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

def stockTrasferRaw(request, pk=None):
    godowns = Godown_raw_material.objects.all()

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        
        try:
            # get te selected source godown
            selected_source_godown_id = request.GET.get('selected_godown_id')
            
            # destination godown options which exclude godown selcted in source godown
            destination_godowns_queryset = Godown_raw_material.objects.exclude(pk = selected_source_godown_id)
            
            destination_godowns = {}

            for records in destination_godowns_queryset:
                destination_godowns[records.id] = records.godown_name_raw
            
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
            
            # get the shade of the selected item
            item_shades_of_selected_item = item_color_shade.objects.filter(items=item_name_value)

            #shades of selected item
            item_shades = {}

            # quantity of all shades of the selected item in all the godowns
            items_shade_quantity_in_godown = {}

            #loop through the itemshade of item   
            for x in item_shades_of_selected_item:
                # in the through table to with the selected shade of the selected item and selected godown
                shades_of_item_in_selected_godown = item_godown_quantity_through_table.objects.filter(godown_name = selected_source_godown_id, Item_shade_name = x.id)
        
                # loop through the filtered queryset of shades in the godown and make 
                # item_shade dict to send in front end 
                for x in shades_of_item_in_selected_godown:

                    shade_name = x.Item_shade_name.item_shade_name
                    shade_id = x.Item_shade_name.id
                    item_shades[shade_id] = shade_name

                    # quantity of shade in godown
                    item_id = x.Item_shade_name.id
                    items_shade_quantity_in_godown[item_id] = x.quantity


            # item color and item_per 
            item_color = None
            item_per = None


            if item_name_value is not None:
                item_name_value = int(item_name_value)

                # get the item 
                items =  get_object_or_404(Item_Creation ,id = item_name_value)
            
                item_color = items.Item_Color.color_name
                item_per = items.unit_name_item.unit_name


            # quantity of the selected shade in that godown 
            shade_quantity = 0
            selected_shade = request.GET.get('selected_shade_id')
            
            if selected_shade is not None and selected_source_godown_id is not None:
                selected_shade = int(selected_shade)
                selected_source_godown_id = int(selected_source_godown_id)

                quantity_get = item_godown_quantity_through_table.objects.filter(Item_shade_name = selected_shade, godown_name = selected_source_godown_id).first()
                shade_quantity  = quantity_get.quantity
            
            
            return JsonResponse({'items_in_godown': items_in_godown, 'item_shades':item_shades,
                                    'item_color':item_color,'item_per':item_per,'items_shade_quantity_in_godown':items_shade_quantity_in_godown,
                                    'shade_quantity':shade_quantity,'destination_godowns':destination_godowns})
        

        except Exception as e:
            messages.error(request, f'An Error occoured {e}')
            logger.error(f'An Error occoured in stock transfer raw{e}')


    if pk:
        raw_transfer_instance = get_object_or_404(RawStockTransferMaster,voucher_no=pk)
        formset  = raw_material_stock_trasfer_items_formset(request.POST or None, instance = raw_transfer_instance)
        source_godown_items = item_godown_quantity_through_table.objects.filter(godown_name = raw_transfer_instance.source_godown.id)

    else:
        source_godown_items = None
        raw_transfer_instance = None
        formset  = raw_material_stock_trasfer_items_formset(request.POST or None,instance = raw_transfer_instance)


    masterstockform = raw_material_stock_trasfer_master_form(request.POST or None, instance = raw_transfer_instance)


    if request.method == 'POST':
        print(request.POST)
        formset.forms = [form for form in formset if form.has_changed()]


        if masterstockform.is_valid() and formset.is_valid():
            masterforminstance = masterstockform.save(commit=False)
            masterforminstance.save()
            
            # check and delete forms marked for deleting 
            for form in formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()


            for form in formset:
                if form.is_valid():
                    if not form.cleaned_data.get('DELETE'):  # to check if form is not marked for deleting, not checked forms that are marked for deleting will be saved again 
                        
                        transfer_instance = form.save(commit=False)
                        transfer_instance.master_instance = masterforminstance # loop through each form in formset to attach the instance of masterforminstance with each form in the formset
                        transfer_instance.save()

            return redirect('stock-transfer-raw-list')


    context = {'masterstockform':masterstockform,'formset':formset,'godowns':godowns,'source_godown_items':source_godown_items}

    return render(request,'misc/stock_transfer_raw.html', context=context)


def stockTrasferRawList(request):

    stocktrasferall = RawStockTransferMaster.objects.all()

    return render(request,'misc/stock_transfer_raw_list.html',{'stocktrasferall':stocktrasferall})


def stockTrasferRawDelete(request,pk):
    stocktrasferinstance =  get_object_or_404(RawStockTransferMaster,pk = pk)
    stocktrasferinstance.delete()
    return redirect('stock-transfer-raw-list')

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
                                  'item_gst_out':item_gst_out,'party_gst_no':party_gst_no})

    if request.method == 'POST':
        
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
                                
                                    row_prefix_id = popup_godown_data.get('prefix_id')

                                    if row_prefix_id == form_prefix_number:
                                        
                                        shade_id = int(popup_godown_data.get('shade_id'))
                                        prefix_id =  int(popup_godown_data.get('prefix_id'))
                                        primarykey = int(popup_godown_data.get('primary_id'))
                                        old_item_shade = int(old_item_shade)
                                        
                                        #function to update popup data on main submit only 
                                        purchasevoucherpopupupdate(popup_godown_data,shade_id,prefix_id,primarykey,old_item_shade)
                                        
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
def purchasevoucherpopup(request,shade_id,prefix_id,unique_id=None,primarykey=None,item_rate=None):
    
    if item_rate != None:
        item_rate_value = decimal.Decimal(item_rate)
    else:
        item_rate_value = None
    
   
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
                                'formset': formset,'unique_id': unique_id, 'shade_id': shade_id,'item_rate_value':item_rate_value,
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
                'godowns': godowns, 'item': item, 'item_shade': item_shade, 'formset': formset, 'item_rate_value':item_rate_value,
                'unique_id': unique_id, 'shade_id': shade_id, 'errors': formset.errors,'prefix_id':prefix_id, 'primary_key':primarykey
            }
            return render(request, 'accounts/purchase_popup.html', context)
        
    return render(request, 'accounts/purchase_popup.html' ,{'godowns':godowns,'item':item,'shade_id': shade_id,
                                                            'item_shade':item_shade,'formset':formset,'item_rate_value':item_rate_value,
                                                            'unique_id':unique_id,'prefix_id':prefix_id, 'primary_key':primarykey})


def purchasevouchercreategodownpopupurl(request):
    shade_id = request.GET.get('selected_shade')
    unique_id = request.GET.get('unique_invoice_row_id')
    primary_key = request.GET.get('purchase_id')
    prefix_id  = request.GET.get('prefix_id')
    item_instance = item_color_shade.objects.get(id=shade_id)
    item_rate = item_instance.rate
    print(item_rate)

    #if pk is there in ajax then it generates url for update if unique id is there in rquest then it generates url with unique key
    if primary_key is not None:
        popup_url = reverse('purchase-voucher-popup-update', args=[shade_id,prefix_id,primary_key])
        
    elif unique_id is not None:
        popup_url = reverse('purchase-voucher-popup-create', args=[shade_id,prefix_id,item_rate,unique_id])
        
    else:
        popup_url = None
    

    return JsonResponse({'popup_url':popup_url})


def purchasevoucherlist(request):
    purchase_invoice_list = item_purchase_voucher_master.objects.all()
    return render(request,'accounts/purchase_invoice_list.html',{'purchase_invoice_list':purchase_invoice_list})


def purchasevoucherdelete(request,pk):
    purchase_invoice_pk = get_object_or_404(item_purchase_voucher_master,pk=pk)
    print(pk)
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

    queryset =  gst.objects.all()

    gst_search = request.GET.get('gst_search','')

    if gst_search != "":
        queryset =  gst.objects.filter(gst_percentage__contains = gst_search)





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
                
                return JsonResponse({"gst_updated": list(gst_updated)})
        else:
            return render(request,template_name,{'form':form, 'title':title, 'gsts':queryset})

    return render(request,template_name,{'form':form, 'title':title, 'gsts':queryset})






def gst_delete(request,pk):
    gst_pk = gst.objects.get(pk=pk)
    gst_pk.delete()
    messages.success(request,'GST deleted')
    return redirect('gst-create-list')



def fabric_finishes_create_update(request, pk = None):
    queryset =  FabricFinishes.objects.all()

    fabric_finishes_search = request.GET.get('fabric_finishes_search','')

    if fabric_finishes_search != '':
        queryset =  FabricFinishes.objects.filter(fabric_finish__icontains = fabric_finishes_search)


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
            
            return render(request,template_name,{'form':form,'title':title,'fabricfinishes':queryset,'fabric_finishes_search':fabric_finishes_search})

    return render(request,template_name,{'form':form,'title':title,'fabricfinishes':queryset,'fabric_finishes_search':fabric_finishes_search})



def fabric_finishes_delete(request,pk):
    fabric_finish =  FabricFinishes.objects.get(pk=pk)
    fabric_finish.delete()
    messages.success(request,'fabric finish deleted.')
    return redirect('fabric-finishes-create-list')


def packaging_create_update(request, pk = None):
    
    queryset =  packaging.objects.all()

    packaging_search = request.GET.get('packaging_search','')

    if packaging_search != '':
        queryset =  packaging.objects.filter(packing_material__icontains = packaging_search)


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
        form = packaging_form(request.POST ,instance = packaging_instance)
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
            
            return render(request, template_name ,{'form':form,'title':title,'packaging_all':queryset}) 

    return render(request, template_name ,{'form':form,'title':title,'packaging_all':queryset})





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
        product2item_instances = product_2_item_through_table.objects.filter(
            PProduct_pk__Product__Product_Refrence_ID=product_refrence_id,
              common_unique = False).select_related('PProduct_pk','Item_pk','PProduct_pk__PProduct_color').order_by('row_number')
        
        formset_single = Product2ItemFormset(queryset=product2item_instances , prefix='product2itemuniqueformset')


        # query for filtering all the common items in all the products in the refrence_id after that :
        #It orders by Item_pk first, so all records with the same Item_pk are grouped together.
        #Within each group of Item_pk, it orders by id.
        #distinct('Item_pk') will keep the first record of each group (based on the smallest id within that group).
        
        
        distinct_product2item_commmon_instances = product_2_item_through_table.objects.filter(
            PProduct_pk__Product__Product_Refrence_ID=product_refrence_id, common_unique = True).order_by(
                'Item_pk', 'id','row_number').distinct('Item_pk').select_related('PProduct_pk','Item_pk')

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
                        if form.instance.id: # check if there is instance before attempting to delete
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
def viewproduct2items_configs(request, product_sku):
    try:
        product2item_instances = product_2_item_through_table.objects.filter(PProduct_pk__PProduct_SKU=product_sku)
        product2item_instances_first = product_2_item_through_table.objects.filter(PProduct_pk__PProduct_SKU=product_sku).first()
        
        context = {
            'product2item_instances': product2item_instances,
            'product2item_instances_first': product2item_instances_first
        }

        return render(request, 'production/product2itemsconfigview.html', context)

    except product_2_item_through_table.DoesNotExist:
        return render(request, 'production/product2itemsconfigview.html', {
            'error_message': f'No items found for product SKU: {product_sku}'})

    except DatabaseError as e:
        # Handle database errors
        return HttpResponseServerError(f'A database error occurred: {e}')

    except Exception as e:
        # Handle any other unexpected errors
        return HttpResponseServerError(f'An unexpected error occurred: {e}')
    




def purchaseordercreateupdate(request,pk=None):
    
    try:
        ledger_party_names = Ledger.objects.filter(under_group__account_sub_group = 'Sundray Debtor(we sell)')
        products = Product.objects.all()

        raw_material_godowns = Godown_raw_material.objects.all()

        # on update instance is fetched by pk which is used for form and formset 
        if pk:
            instance = get_object_or_404(purchase_order,pk=pk)
            model_name = instance.product_reference_number.Model_Name

        else:
            instance = None
            model_name = None
        
        formset = purchase_order_product_qty_formset(request.POST or None, instance=instance)
        form = purchase_order_form(instance=instance)

    except Exception as e:
        logger.error(f'An Exception Occoured {e}')


    if request.method == 'POST':
        print(request.POST)
        # both forms are submitted indivially depends on name of submitted button
        # (on create only form-1 is visble to the user as formsets are created on submission of form-1 using signals)
        if 'submit-form-1' in request.POST:
            form = purchase_order_form(request.POST, instance=instance)
        
            if form.is_valid():
                try:
                    
                    form_instance = form.save(commit=False)
                    form_instance.balance_number_of_pieces = form.instance.number_of_pieces
                    form_instance.save()
                    logger.info(f'Purchase invoice created-updated-{form.instance.id}')
                    # on submission of form-1, form-2 is rendered with form-1 instance
                    return redirect(reverse('purchase-order-update', args=[form.instance.id]))
                
                except ValidationError as val_err:
                    logger.error(f'Validation error: {val_err} - {form.errors}')

                except DatabaseError as db_err:
                    logger.error(f'Database error during formset save: {db_err}')

                except Exception as e:
                    logger.error(f'Unexpected error during form save: {e}')
            else:
                logger.error(f'Purchase Order Quantities updated error-{form.instance.id} - {form.errors}')
            

        if 'submit-form-2' in request.POST:

            try:
                formset = purchase_order_product_qty_formset(request.POST or None, instance=instance)
                
                if formset.is_valid():
                    try:
                        formset.save()
                        # set the status to 2
                        for form in formset:
                            p_o_instance = form.instance.purchase_order_id  # get FK instance from form instance
                            if p_o_instance.process_status == '1':  # if process_status in parent form is 1
                                p_o_instance.process_status = '2'  # change the status to 2
                                p_o_instance.save()  # save the parent form instance
                                

                        messages.success(request, 'Purchase Order Quantities updated successfully.')
                        logger.info(f'Purchase Order Quantities updated-{form.instance.id}')

                        #return redirect(reverse('purchase-order-rawmaterial', args=[instance.id, instance.product_reference_number.Product_Refrence_ID]))
                        return redirect('purchase-order-raw-material-list')

                    except DatabaseError as db_err:
                        logger.error(f'Database error during form save: {db_err}')
                        messages.error(request, 'A database error occurred during form save.')

                    except Exception as e:
                        logger.error(f'Unexpected error during form save: {e}')
                        messages.error(request, 'An unexpected error occurred during form save.')
                else:
                    # Log formset errors
                    print(formset.errors)
                    logger.error(f'Purchase Order Quantities update error - {formset.errors} {formset.non_form_errors()}')
                    messages.error(request, f'There were errors in the form. Please correct them and try again.')

            except ValidationError as val_err:
                logger.error(f'Validation error: {val_err}-{formset.errors}')
                messages.error(request, f'Validation error: {val_err}')

            except Exception as e:
                logger.error(f'Exception occurred: {e}')
                messages.error(request, f'An exception occurred: {e}') 
        

    return render(request,'production/purchaseordercreateupdate.html',{'form':form ,'formset':formset,'raw_material_godowns':raw_material_godowns,
                                                                          'ledger_party_names':ledger_party_names,
                                                                          "products":products,'model_name':model_name})



def purchaseorderlist(request):
    purchase_orders = purchase_order.objects.all()
    return render(request,'production/purchaseorderlist.html',{'purchase_orders': purchase_orders})



def purchaseorderdelete(request,pk):
    try:
        instance = get_object_or_404(purchase_order, pk = pk)
        instance.delete()
        logger.info(f"Purchase Order with order no - {instance.purchase_order_number} was deleted")
        messages.success(request,f'Purchase order with order no - {instance.purchase_order_number} was deleted')
        
    except exception as e:
        messages.error(request,f'Cannot delete {instance.purchase_order_number} - {e}.')
        logger.error(f"Cannot delete {instance.purchase_order_number} - {e}.")
    return redirect('purchase-order-list')
     


def purchaseorderrawmaterial(request,p_o_pk,prod_ref_no):
    
    purchase_order_instance = get_object_or_404(purchase_order, pk=p_o_pk)

    form = purchase_order_form(instance = purchase_order_instance)

    product_refrence_no = prod_ref_no
    product_2_items_instances = product_2_item_through_table.objects.filter(
                            PProduct_pk__Product__Product_Refrence_ID = product_refrence_no).order_by(
                                'Item_pk','id').distinct('Item_pk')

    model_name = purchase_order_instance.product_reference_number.Model_Name

    physical_stock_all_godowns = {}

    for item in product_2_items_instances:
        item_id = item.Item_pk
        item_name = item.Item_pk.item_name
        item_quantity = 0
        item_godowns = item_godown_quantity_through_table.objects.filter(Item_shade_name__items = item_id,
                                        godown_name =purchase_order_instance.temp_godown_select) #later filter by godown also after checking user godown location
        
        if item_godowns:
            for query in item_godowns:
                item_quantity = item_quantity + query.quantity
                physical_stock_all_godowns[item_name] = str(item_quantity)

        else:
            physical_stock_all_godowns[item_name] = str(item_quantity)

    purchase_order_raw_formset = purchase_order_raw_product_qty_formset(request.POST or None, instance = purchase_order_instance)

    # for create (to check child instances of p_o_id is not present)(in this case will render initial data)
    if not purchase_order_instance.raw_materials.all():
        
        physical_stock_all_godown_json = json.dumps(physical_stock_all_godowns) # convert python dict to json and send only on create on update it will be None

        initial_data = []
        for query in product_2_items_instances:
            rate_first = query.Item_pk.shades.order_by('id').first() # get the rate of the first shade of the color 
            
            # for fortend use to mulitply total proccessed qty with consumption for common item
            if query.common_unique == True:
                product_color_or_common_item = 'Common Item'
                product_sku_or_common_item = 'Common Item'

            else:
                product_color_or_common_item = query.PProduct_pk.PProduct_color
                product_sku_or_common_item = query.PProduct_pk.PProduct_SKU

            initial_data_dict = {'product_sku': product_sku_or_common_item,
                                'product_color' : product_color_or_common_item,
                                'material_name':query.Item_pk.item_name,
                                'rate':rate_first.rate,
                                'panha':query.Item_pk.Panha,
                                'units':query.Item_pk.Units,
                                'g_total':query.grand_total,
                                'consumption':'0',
                                'total_comsumption':'0',
                                'physical_stock':'0',
                                'balance_physical_stock':'0'}
            
            initial_data.append(initial_data_dict)

        purchase_order_raw_product_sheet_formset = inlineformset_factory(purchase_order, purchase_order_for_raw_material, form=purchase_order_raw_product_sheet_form, extra=len(initial_data) if initial_data else 0, can_delete=False)

        purchase_order_raw_sheet_formset = purchase_order_raw_product_sheet_formset(initial=initial_data, instance=purchase_order_instance)


    # for update(to check child instances of p_o_id is avaliable means form is on update)
    elif purchase_order_instance.raw_materials.all():

        physical_stock_all_godown_json = None # send only on create on update it will be None as saved data will be rendered


        purchase_order_raw_product_sheet_formset = inlineformset_factory(purchase_order, purchase_order_for_raw_material, form=purchase_order_raw_product_sheet_form, extra=0, can_delete=False)

        purchase_order_raw_sheet_formset = purchase_order_raw_product_sheet_formset(instance=purchase_order_instance)

    
    if request.method == 'POST':
        purchase_order_raw_sheet_formset = purchase_order_raw_product_sheet_formset(request.POST, instance=purchase_order_instance)

        try:
            if purchase_order_raw_formset.is_valid() and purchase_order_raw_sheet_formset.is_valid():
                
                try:
                    purchase_order_raw_formset.save()
                    purchase_order_raw_sheet_formset.save()
                    
                    for form in purchase_order_raw_sheet_formset:
                        po_form_instance = form.instance.purchase_order_id  # get FK instance from form instance
                        if po_form_instance.process_status == '2':   # if process_status in parent form is 2 
                            po_form_instance.process_status = '3'  # change the status to 3
                            po_form_instance.save()  # save the parent form instance 

                    #return(redirect(reverse('purchase-order-cutting-list',args = [purchase_order_instance.id, purchase_order_instance.product_reference_number.Product_Refrence_ID])))
                    return redirect('purchase-order-raw-material-list')
                
                except ValueError as ve:
                    messages.error(request,f'Error Occured - {ve}')

                except exception as e:
                    messages.error(request,f'Exception Occured - {e}')
                
                return render(request,'production/purchaseorderrawmaterial.html',{'form': form ,'model_name':model_name,
                                                                        'purchase_order_raw_formset':purchase_order_raw_formset,
                                                                        'purchase_order_raw_sheet_formset':purchase_order_raw_sheet_formset,
                                                                        'physical_stock_all_godown_json':physical_stock_all_godown_json})

            
            else:
                print(purchase_order_raw_formset.errors,purchase_order_raw_sheet_formset.errors)
                raise ValidationError("No products found for the given reference ID.")
                # messages.error(request,f' Please enter correct Procurement color wise QTY {purchase_order_raw_sheet_formset.errors}-{purchase_order_raw_sheet_formset.errors}')
                # return render(request,'production/purchaseorderrawmaterial.html',{'form': form ,'model_name':model_name,
                #                                                         'purchase_order_raw_formset':purchase_order_raw_formset,
                #                                                         'purchase_order_raw_sheet_formset':purchase_order_raw_sheet_formset,
                #                                                         'physical_stock_all_godown_json':physical_stock_all_godown_json})
        except ValidationError as ve:
                messages.error(request,f' Please enter correct Procurement color wise QTY {ve}')
        
        except exception as e:
            messages.error(request,f' An exception occoured {e}')



    return render(request,'production/purchaseorderrawmaterial.html',{'form': form ,'model_name':model_name,
                                                                      'purchase_order_raw_formset':purchase_order_raw_formset,
                                                                      'purchase_order_raw_sheet_formset':purchase_order_raw_sheet_formset,
                                                                      'physical_stock_all_godown_json':physical_stock_all_godown_json})


def purchase_order_for_raw_material_list(request):
    # to know if related multiple records are created or not - create temp column named raw_material_count and 
    # count the records present in related model and then filter that column if more then 1 record is present
    purchase_orders_pending = purchase_order.objects.annotate(raw_material_count=Count('raw_materials')).filter(raw_material_count__lt=1)
    purchase_orders_completed = purchase_order.objects.annotate(raw_material_count=Count('raw_materials')).filter(raw_material_count__gt=0)


    return render(request,'production/purchase_order_for_raw_material_list.html',
                  {'purchase_orders_pending': purchase_orders_pending,
                   'purchase_orders_completed':purchase_orders_completed})



def purchase_order_for_raw_material_delete(request,pk):
    purchase_order_raw_instances = purchase_order_for_raw_material.objects.filter(purchase_order_id=pk)

    for instances in purchase_order_raw_instances:
        instances.delete()

    return redirect('purchase-order-raw-material-list')



def purchaseordercuttingcreateupdate(request,p_o_pk,prod_ref_no,pk=None):

    if pk:
        purchase_order_cutting_instance = get_object_or_404(purchase_order_raw_material_cutting, pk=pk)
    else:
        purchase_order_cutting_instance = None

    labour_all = factory_employee.objects.all()

    # purchase_order_instance
    purchase_order_instance = get_object_or_404(purchase_order, pk=p_o_pk)

    # purchase_order_raw_material_instances
    purchase_order_raw_instances = purchase_order_for_raw_material.objects.filter(purchase_order_id=p_o_pk)


    #purchase_order_to_product_instances
    purchase_order_to_product_instances = purchase_order_to_product.objects.filter(purchase_order_id=p_o_pk)

    # purchase_order_form
    form = purchase_order_form(instance = purchase_order_instance)

    current_godown = form.instance.temp_godown_select

    # cutting form for that purchase order (this form data is submitted only)(for create and view/update page)
    purchase_order_cutting_form = purchase_order_raw_material_cutting_form(request.POST or None, instance=purchase_order_cutting_instance)

    # for create page initial data is denndered 
    if not pk:

        # initial data for purchase_order_cutting items
        initial_data = []
        for purchase_items_raw in purchase_order_raw_instances:

            godown_quantity_subquery = item_godown_quantity_through_table.objects.filter(godown_name= current_godown,
                                                                                    Item_shade_name=OuterRef('pk')).values('quantity')[:1]
            # Filter and annotate the item_color_shade queryset
            material_color_shade_query = item_color_shade.objects.filter(items__item_name=purchase_items_raw.material_name).annotate(
                    godown_qty=Coalesce(Subquery(godown_quantity_subquery, output_field=DecimalField()),  decimal.Decimal('0')))
            
            current_physical_stock = 0
            for shade in material_color_shade_query:
                current_physical_stock = current_physical_stock + shade.godown_qty


            initial_data_dict = {
                'product_sku': purchase_items_raw.product_sku,
                'product_color' : purchase_items_raw.product_color,
                'material_name' : purchase_items_raw.material_name,
                'material_color_shade': material_color_shade_query.order_by('-godown_qty'), # sorting shades based on quantity
                'fabric_non_fab': material_color_shade_query.first().items.Fabric_nonfabric, #not in database table for computational purpose
                'rate' : purchase_items_raw.rate,
                'panha' : purchase_items_raw.panha,
                'units' : purchase_items_raw.units,
                'g_total' : purchase_items_raw.g_total,
                'consumption' : purchase_items_raw.consumption,
                'total_comsumption' :'0',
                'physical_stock' : current_physical_stock,
                'balance_physical_stock' : '0',
            }
            
            initial_data.append(initial_data_dict)

        
        # production sheet for that cutting order of the purchase order (inline factory for below form)
        purchase_order_for_raw_material_cutting_items_formset = inlineformset_factory(purchase_order_raw_material_cutting, 
                                                                                      purchase_order_for_raw_material_cutting_items, 
                                                                                      form=purchase_order_for_raw_material_cutting_items_form,
                                                                                      formset=Basepurchase_order_for_raw_material_cutting_items_form, 
                                                                                      extra=len(initial_data), 
                                                                                      can_delete=False)


        # formset creation from  purchase_order_for_raw_material_cutting_items_formset (this form data is submitted only)(for get request)
        purchase_order_for_raw_material_cutting_items_formset_form = purchase_order_for_raw_material_cutting_items_formset(initial=initial_data)


        # intial data for purchase_order_to_product formset
        initial_data_p_o_to_items = []

        for instances in purchase_order_to_product_instances:
            initial_data_dict = {
                'product_color': instances.product_id.PProduct_color,
                'product_sku': instances.product_id.PProduct_SKU,
                'order_quantity': instances.order_quantity,
                'process_quantity': instances.process_quantity,
                'cutting_quantity': '0',
            }

            initial_data_p_o_to_items.append(initial_data_dict)

        # production sheet for that product_to purchase order of the purchase order (inline factory for below form)
        purchase_order_to_product_formset = inlineformset_factory(purchase_order_raw_material_cutting, 
                                                                  purchase_order_to_product_cutting,
                                                                    form=purchase_order_to_product_cutting_form,
                                                                      extra=len(initial_data_p_o_to_items),
                                                                      can_delete=False)

        purchase_order_to_product_formset_form = purchase_order_to_product_formset(initial= initial_data_p_o_to_items)

    # for view page 
    elif pk:

        purchase_order_for_raw_material_cutting_items_formset = inlineformset_factory(purchase_order_raw_material_cutting,
                                                                                       purchase_order_for_raw_material_cutting_items,
                                                                                         form=purchase_order_for_raw_material_cutting_items_form, 
                                                                                         extra=0, can_delete=False)
        
        purchase_order_for_raw_material_cutting_items_formset_form = purchase_order_for_raw_material_cutting_items_formset(instance=purchase_order_cutting_instance)


        # production sheet for that product_to purchase order of the purchase order (inline factory for below form)
        purchase_order_to_product_formset = inlineformset_factory(purchase_order_raw_material_cutting, purchase_order_to_product_cutting, 
                                                                  form=purchase_order_to_product_cutting_form, extra=0, can_delete=False)
        
        purchase_order_to_product_formset_form = purchase_order_to_product_formset(instance=purchase_order_cutting_instance)
        
    if request.method == 'POST':
        
        # formset creation from  purchase_order_for_raw_material_cutting_items_formset (this form data is submitted only)(for post request)
        purchase_order_for_raw_material_cutting_items_formset_form = purchase_order_for_raw_material_cutting_items_formset(request.POST)

        # formset for purchase_order_to_products_cutting for POST request
        purchase_order_to_product_formset_form = purchase_order_to_product_formset(request.POST)

        if purchase_order_cutting_form.is_valid() and purchase_order_to_product_formset_form.is_valid() and purchase_order_for_raw_material_cutting_items_formset_form.is_valid():
            try:
                # cutting form save
                cutting_form_instance = purchase_order_cutting_form.save()
                # change the status in purchase order model 
                if cutting_form_instance.purchase_order_id.process_status == '3':
                    cutting_form_instance.purchase_order_id.process_status = '4'
                    cutting_form_instance.purchase_order_id.save()
                

                # purchase_order to product formset 
                for form in purchase_order_to_product_formset_form:

                    if form.is_valid(): 
                        try:
                            p_o_to_order_form_instance = form.save(commit = False)
                            p_o_to_order_form_instance.purchase_order_cutting_id = cutting_form_instance
                            p_o_to_order_form_instance.save()

                            # reduce the process quantity form purchase_order_to_products model
                            product_sku = p_o_to_order_form_instance.product_sku
                            processed_qty = p_o_to_order_form_instance.cutting_quantity

                            p_o_id = p_o_to_order_form_instance.purchase_order_cutting_id.purchase_order_id
                           
                            purchase_order_products = purchase_order_to_product.objects.filter(purchase_order_id =p_o_id,product_id =product_sku).first()

                            if purchase_order_products:
                                purchase_order_products.process_quantity =  purchase_order_products.process_quantity - processed_qty
                                purchase_order_products.save()

                            else:
                                logger.error(f'Product {product_sku} not found in purchase order {p_o_id}')
                                messages.error(request, f'Product {product_sku} not found in the purchase order.')

                        except Exception as e:
                            logger.error(f'Error processing product form: {e}')
                            messages.error(request, f'An error occurred while processing the product form: {e}')


                # purchase_order_cutting_items formset
                for form in purchase_order_for_raw_material_cutting_items_formset_form:
                    if form.is_valid(): 
                        try:
                            form_instance = form.save(commit=False)
                            form_instance.purchase_order_cutting = cutting_form_instance
                            form_instance.save()
                        

                        except ValidationError as ve:
                            logger.error(f'Error with: {e}')

                        except Exception as e:
                            logger.error(f'Error processing raw material form: {e}')
                            messages.error(request, f'An error occurred while processing the raw material form: {e}')
                    
                    
                # updating balance quantity of purchase order form 
                processed_quantity = int(request.POST['processed_qty'])
                qty_to_process = cutting_form_instance.purchase_order_id.balance_number_of_pieces  # get the quanitty from purchase_order
                qty_to_process_minus_processed_qty = qty_to_process - processed_quantity  # reduce the purchase_order_qty with the processed qty
                cutting_form_instance.purchase_order_id.balance_number_of_pieces = qty_to_process_minus_processed_qty  # assign the value
                cutting_form_instance.purchase_order_id.save() # save changes

                messages.success(request, f'Cutting Order Created SuccessFully')
                return(redirect(reverse('purchase-order-cutting-list', args = [cutting_form_instance.purchase_order_id.id, cutting_form_instance.purchase_order_id.product_reference_number.Product_Refrence_ID])))


            except ValidationError as val_err:
                logger.error(f'Validation error: {val_err}')
                messages.error(request, f'Validation error: {val_err}')


            except DatabaseError as db_err:
                logger.error(f'Database error: {db_err}')
                messages.error(request, f'Database error: {db_err}')


            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                messages.error(request, f'An unexpected error occurred: {e}')

        else:
            # messages.error(request,f'Purchase Order Form Errors {purchase_order_cutting_form.errors}')
            # messages.error(request,f'Purcahse Order To product Cutting Forms Errors {purchase_order_to_product_formset_form.errors}')
            # messages.error(request,f'Raw Material Cutting Items Formset Errors {purchase_order_for_raw_material_cutting_items_formset_form.errors}')

            # messages.error(request,f'Purcahse Order To product Cutting Forms Errors {purchase_order_to_product_formset_form.non_form_errors()}')
            # messages.error(request,f'Raw Material Cutting Items Formset Errors {purchase_order_for_raw_material_cutting_items_formset_form.non_form_errors()}')


            return render(request,'production/purchase_order_cutting.html',{'form':form,'labour_all':labour_all,'purchase_order_cutting_form':purchase_order_cutting_form,'p_o_pk':p_o_pk,
                                                                    'purchase_order_to_product_formset_form':purchase_order_to_product_formset_form,
                                                                     'purchase_order_for_raw_material_cutting_items_formset_form':purchase_order_for_raw_material_cutting_items_formset_form})


    return render(request,'production/purchase_order_cutting.html',{'form':form,'labour_all':labour_all,'purchase_order_cutting_form':purchase_order_cutting_form,'p_o_pk':p_o_pk,
                                                                    'purchase_order_to_product_formset_form':purchase_order_to_product_formset_form,
                                                                     'purchase_order_for_raw_material_cutting_items_formset_form':purchase_order_for_raw_material_cutting_items_formset_form})



def purchaseordercuttinglist(request,p_o_pk,prod_ref_no):
    p_o_cutting_order_all =  purchase_order_raw_material_cutting.objects.filter(purchase_order_id = p_o_pk)
    Purchase_order_no = purchase_order.objects.get(id=p_o_pk)
    return render(request,'production/purchaseordercuttinglist.html', {'p_o_cutting_order_all':p_o_cutting_order_all, 'p_o_number':Purchase_order_no, 'prod_ref_no':prod_ref_no, 'p_o_pk':p_o_pk})




def purchaseordercuttinglistall(request):
    purchase_orders_cutting_pending = purchase_order.objects.annotate(raw_material_count=Count('raw_materials')).filter(raw_material_count__gt=0).filter(balance_number_of_pieces__gt=0)
    purchase_orders_cutting_completed = purchase_order.objects.filter(balance_number_of_pieces=0)
    return render(request,'production/purchaseordercuttinglistall.html', {'purchase_orders_cutting_pending':purchase_orders_cutting_pending,'purchase_orders_cutting_completed':purchase_orders_cutting_completed})



def purchaseordercuttingpopup(request,cutting_id):

    if cutting_id:
        cutting_order_instance = purchase_order_raw_material_cutting.objects.get(raw_material_cutting_id = cutting_id)
    else:
        cutting_order_instance = None

    formset = purchase_order_cutting_approval_formset(request.POST or None, instance=cutting_order_instance)

    if request.method == 'POST':
        formset.forms = [form for form in formset.forms if form.has_changed()]
        if formset.is_valid():
            if any(form.has_changed() for form in formset): # if all the forms are not changed below code will not get executed
                formset_instance = formset.save(commit=False)

                # get the cutting instance of approval instance
                raw_material_cutting_instance = purchase_order_raw_material_cutting.objects.get(raw_material_cutting_id=cutting_id)

                # old approved qty
                old_total_approved_qty_total = raw_material_cutting_instance.approved_qty


                # create an instance in labour workout master of the cutting instance
                labour_workout_master_instance = labour_workout_master.objects.create(purchase_order_cutting_master=raw_material_cutting_instance)

                for form in formset_instance:
                    p_o_to_cutting_instance = purchase_order_to_product_cutting.objects.get(id = form.id) # p_o_cutting_instance
                    old_total_approved_qty_diffrence  =  form.approved_pcs - p_o_to_cutting_instance.approved_pcs  # current qty - old qty to get the diffrence in qty
                    form.approved_pcs_diffrence = old_total_approved_qty_diffrence  # assign the difrence qty to form variable
                    old_total_approved_qty_total = old_total_approved_qty_total + old_total_approved_qty_diffrence # add the diffrence qty to total qty of parent model
                    form.save() # save the instance model
                    
                    # create new instance of the data in product_to_item_labour_workout with the created labour_workout_master_instance as parent model
                    product_to_item_labour_workout.objects.create(labour_workout=labour_workout_master_instance,
                                                                product_color=form.product_color,product_sku=form.product_sku,
                                                                pending_pcs = old_total_approved_qty_diffrence,processed_pcs=0)

                raw_material_cutting_instance.approved_qty = old_total_approved_qty_total # save the total diffrence total qty to parent model
                raw_material_cutting_instance.save() # save the parent model

            # JavaScript to close the popup window
            close_window_script = """
            <script>
            window.opener.location.reload(true);  // Reload parent window if needed
            window.close();  // Close current window
            </script>
            """

            return HttpResponse(close_window_script)
        else:
            return render(request,'production/purchaseordercuttingpopup.html', {'formset':formset})

            
    return render(request,'production/purchaseordercuttingpopup.html', {'formset':formset})





def labourworkoutlistall(request):
    labour_workout_pending = labour_workout_master.objects.all()
    return render(request,'production/labourworkoutlistall.html', {'labour_workout_pending':labour_workout_pending})


def labourworkoutsingle(request,pk):
    labourworkoutinstance = labour_workout_master.objects.get(id=pk)
    ledger_labour_instances = Ledger.objects.filter(types = 'labour')

    # labour workout masterform
    labour_work_out = labour_workout_master_form(request.POST or None, instance = labourworkoutinstance)

    # product 2 item form
    product_to_item_formset = labour_workout_product_to_items_formset(request.POST or None, instance = labourworkoutinstance)

    raw_material_cutting_items_instances = purchase_order_for_raw_material_cutting_items.objects.filter(purchase_order_cutting = labourworkoutinstance.purchase_order_cutting_master)

    initial_data_dict = []
    for instance in raw_material_cutting_items_instances:
        data = {
            'product_sku':instance.product_sku,
            'product_color':instance.product_color,
            'material_name':instance.material_name,
            'material_color_shade':instance.material_color_shade,
            'rate':instance.rate,
            'panha':instance.panha,
            'units':instance.units,
            'g_total':instance.g_total,
            'consumption':instance.consumption,
            'total_comsumption':instance.total_comsumption,
            'physical_stock':instance.physical_stock,
            'balance_physical_stock':instance.balance_physical_stock,

        }
        initial_data_dict.append(data)


    labour_workout_cutting_items_form_formset = inlineformset_factory(labour_workout_master,labour_workout_cutting_items,
                                                                      form = labour_workout_cutting_items_form, 
                                                                      extra=len(initial_data_dict))
    # labour workout items formset
    labour_workout_cutting_items_formset_form =  labour_workout_cutting_items_form_formset(initial = initial_data_dict) 

    if request.method == 'POST':
        labour_workout_cutting_items_formset_form =  labour_workout_cutting_items_form_formset(request.POST) 

        if labour_work_out.is_valid() and product_to_item_formset.is_valid() and labour_workout_cutting_items_form_formset.is_valid():
            labour_work_out.save()
            product_to_item_formset.save()
            labour_workout_cutting_items_form_formset.save()



    return render(request,'production/labourworkoutsingle.html',
                  {'product_to_item_formset':product_to_item_formset,'labour_work_out':labour_work_out,
                   'labour_workout_cutting_items_formset_form':labour_workout_cutting_items_formset_form,
                   'ledger_labour_instances':ledger_labour_instances})



#_________________________production-end__________________________________________

#_________________________factory-emp-start_______________________________________


def factory_employee_create_update_list(request,pk=None):
    
    factory_employees = factory_employee.objects.all()
    cutting_rooms =  cutting_room.objects.all()
    if pk:
        title = 'Update'
        instance = get_object_or_404(factory_employee,pk=pk)

    else:
        title = 'Create'
        instance = None
    
    form = factory_employee_form(request.POST or None, instance = instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(request,'Factory Employee created Successfully')
            return redirect('factory-emp-create')
        else:
            messages.error(request,f'Error with form submission {form.errors}')

    return render(request,'production/factory_emp_create_update_list.html', {'form':form,'factory_employees':factory_employees,'title':title,'cutting_rooms':cutting_rooms})


def factoryempdelete(request,pk=None): 
    try:
        instance = get_object_or_404(factory_employee,pk=pk)
        instance.delete()
        messages.success(request,f'Factory Employee {instance.factory_emp_name} was deleted')

    except IntegrityError as e:
        messages.error(request,f'Cannot delete {instance.factory_emp_name} because it is referenced by other objects.')
    return redirect('factory-emp-create')



def cutting_room_create_update_list(request, pk=None):

    if pk:
        instance = cutting_room.objects.get(id = pk)

    else:
        instance = None

    form = cutting_room_form(request.POST or None, instance= instance)

    cutting_rooms = cutting_room.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('cutting_room-create')
    
    return render(request,'production/cuttingroomcreateupdatelist.html', {'form':form,'cutting_rooms':cutting_rooms})


def cuttingroomdelete(request,pk):
    instance = cutting_room.objects.get(pk = pk)
    instance.delete()
    return redirect('cutting_room-create')


#_________________________factory-emp-end_______________________________________


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

    return render(request,'misc/credit_debit_master_report.html',{'all_reports':all_reports})




def godown_stock_raw_material_report_fab_grp(request,g_id,fab_id=None):
    
    # get all the items in the selected godown
    items_in_godown = item_godown_quantity_through_table.objects.filter(godown_name=g_id)
    
    
    Fabric_grp_name = None
    querylist = None

    # fabric report and item report are on the same page only queries are changed
    if fab_id:
        page_id = 'item_page'
    else:
        page_id = 'fabric_page'
    

    if page_id == 'fabric_page':
        # in all the items in godown get their disticnt fabricgrp items (here we get only the items which are in distint fabric grp) 
        fabric_in_godown = items_in_godown.distinct('Item_shade_name__items__Fabric_Group')
        
        list_fab_grp = []

        # in dinstnt items of fab grp get their fab_grp and append in list  
        for fab in fabric_in_godown:
            list_fab_grp.append(fab.Item_shade_name.items.Fabric_Group.id)

        queryset = []

        # now query the fab grp model from the list of distint fab grp in that godown and append in a list 
        for items in list_fab_grp:
            values = Fabric_Group_Model.objects.filter(id=
                    items).filter(items__shades__godown_shades__godown_name=g_id).annotate(total_qty = 
                    Round(Sum('items__shades__godown_shades__quantity'),2),
                    avg_rate=Round(Avg('items__shades__rate'),2)).first()

                    # in query filter fab grp by id then by godown id and annotate total qty of all the items of all fab grp in the godown and avg rate

            queryset.append(values)

    elif page_id == 'item_page':

        # if it is item page (items in selected fab grp)

        Fabric_grp_name = Fabric_Group_Model.objects.get(id=fab_id)

        items_in_fab_grp = Item_Creation.objects.filter(Fabric_Group=fab_id).filter(
            shades__godown_shades__godown_name__id=g_id).annotate(
                total_qty =Round(Sum('shades__godown_shades__quantity')))
                # in query filter item creation with the selctd fabgrp then filter by godown and annotate total_qty of all the items of the selcted fabgrp in the godown 

        querylist = []
        
        # append all the required data from the queryset in a list
        for query in items_in_fab_grp: # item creation model
            item_dict = {}
            item_dict['item_name'] = query.item_name
            item_dict['total_qty'] = query.total_qty

            shades_list = []
            for shade in query.shades.filter(godown_shades__godown_name__id=g_id): # item shades model (filter by g_id while looping)
                shade_dict = {}
                shade_dict['rate'] = shade.rate
                shades_list.append(shade_dict)

                shade_godown_list = []
                for godown_items in shade.godown_shades.filter(godown_name__id=g_id): # item to godown model (filter by g_id while looping)
                    godown_shade_dict = {}
                    shade_dict['item_shade'] = godown_items.Item_shade_name.item_shade_name
                    shade_dict['item_shade_id'] = godown_items.Item_shade_name.id
                    shade_dict['quantity'] = godown_items.quantity
                    shade_godown_list.append(godown_shade_dict)

            item_dict['shades'] = shades_list
            querylist.append(item_dict)
        queryset = items_in_fab_grp

    godown_name = Godown_raw_material.objects.get(id = g_id)
    
    
    return render(request,'reports/godownstockrawmaterialreportfabgrp.html',{'page_id':page_id,
                                                                             'godown_id':g_id,
                                                                             'godown_name':godown_name,
                                                                             'Fabric_grp_name':Fabric_grp_name,
                                                                             'queryset':queryset,
                                                                             'querylist':querylist})


def godown_item_report(request,g_id,shade_id):
    
    godown_name = Godown_raw_material.objects.get(id=g_id)
    shade_name = item_color_shade.objects.get(id=shade_id)

    report_data = []

    # opening quantity report query
    opening_godown_qty = opening_shade_godown_quantity.objects.filter(
        opening_purchase_voucher_godown_item=shade_name, opening_godown_id=godown_name)
    


    # purchase voucher reqport query
    closing_quantity = decimal.Decimal(0.00)
    closing_value = decimal.Decimal(0.00)
    
    # comments in please check notes/ORM_query_dump.txt line no 34
    purchase_voucher_godown_qty = item_purchase_voucher_master.objects.filter(
        purchase_voucher_items__item_shade = shade_name ,purchase_voucher_items__shade_godown_items__godown_id = godown_name).annotate(
            godown_qty_total=Sum('purchase_voucher_items__shade_godown_items__quantity'), item_rate=Round(Avg(
                'purchase_voucher_items__rate')), filter=Q(purchase_voucher_items__shade_godown_items__godown_id = godown_name))
    
    
    
    for godown_qty in opening_godown_qty:

        closing_quantity += godown_qty.opening_quantity
        closing_value += godown_qty.opening_rate * godown_qty.opening_quantity
        report_data.append({
            'date': godown_qty.created_date,
            'particular': 'Opening Balance',
            'voucher_type': '',
            'vch_no': '',
            'inward_quantity': f"{godown_qty.opening_quantity} Meter",
            'inward_value': godown_qty.opening_rate * godown_qty.opening_quantity,
            'outward_quantity': '',
            'outward_value': '',
            'closing_quantity': f"{closing_quantity} Meter",
            'closing_value': closing_value,
            'rate':godown_qty.opening_rate
        })

    for purchase_voucher_item_qty in purchase_voucher_godown_qty:

        closing_quantity += purchase_voucher_item_qty.godown_qty_total
        closing_value += purchase_voucher_item_qty.item_rate * purchase_voucher_item_qty.godown_qty_total
        
        report_data.append({
            'date': purchase_voucher_item_qty.created_date,
            'particular': 'Puchase Voucher',
            'voucher_type': purchase_voucher_item_qty.ledger_type,
            'vch_no': purchase_voucher_item_qty.purchase_number,
            'inward_quantity': f"{purchase_voucher_item_qty.godown_qty_total} Meter",
            'inward_value': purchase_voucher_item_qty.item_rate * purchase_voucher_item_qty.godown_qty_total,
            'outward_quantity': '',
            'outward_value': '',
            'closing_quantity': f"{closing_quantity} Meter",
            'closing_value': closing_value,
            'rate': purchase_voucher_item_qty.item_rate
            })

    return render(request,'reports/godownstockrawmaterialreportsingle.html',{'godoown_name':godown_name,
                                                                             'shade_name':shade_name,'report_data':report_data})


#__________________________reports-end____________________________________



#_______________________authentication View start___________________________


from django.apps import apps
# Import the user model directly
UserModel = apps.get_model(settings.AUTH_USER_MODEL)



def superuser_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func



@superuser_required
def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('user_list')  #Redirect to a list of users or another appropriate page
    else:
        form = CreateUserForm()
    return render(request, 'misc/create_user.html', {'form': form})



@superuser_required
def edit_user_roles(request, user_id):
    user = get_object_or_404(UserModel, id=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Redirect to a list of users or another appropriate page
    else:
        form = UserRoleForm(instance = user)
    return render(request, 'misc/edit_user_roles.html', {'form': form, 'user': user})



@superuser_required
def user_list(request):
    users = UserModel.objects.all()
    return render(request, 'misc/user_list.html', {'users': users})




def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)













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
