from io import BytesIO
from django.contrib.auth.models import User , Group
from django.core.exceptions import ValidationError
import json
from django.contrib.auth.models import auth 
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.utils.timezone import now
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
                                 item_purchase_voucher_master, opening_shade_godown_quantity, packaging, product_2_item_through_table, purchase_voucher_items, set_prod_item_part_name, shade_godown_items,
                                   shade_godown_items_temporary_table)

from .forms import(ColorForm, CreateUserForm, CustomPProductaddFormSet,
                    FabricFinishes_form, ItemFabricGroup, Itemform, LedgerForm,
                     LoginForm,OpeningShadeFormSetupdate, PProductAddForm, PProductCreateForm, ShadeFormSet,
                       StockItemForm, UnitName, account_sub_grp_form, PProductaddFormSet,
                        ProductImagesFormSet, ProductVideoFormSet,purchase_voucher_items_godown_formset_shade_change,
                         gst_form, item_purchase_voucher_master_form,
                           packaging_form, product_main_category_form, 
                            product_sub_category_form, purchase_voucher_items_formset,
                             purchase_voucher_items_godown_formset, purchase_voucher_items_formset_update,
                                shade_godown_items_temporary_table_formset,shade_godown_items_temporary_table_formset_update,
                                Product2ItemFormset,Product2CommonItemFormSet)




def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


#____________________________Production-Product-View-Start__________________________________

def dashboard(request):
    return render(request,'misc/dashboard.html')


#NOTE : in this form one product can be in only one main-category and multiple sub-categories - CURRENTLY USING THIS LOGIC
def edit_production_product(request,pk):
    gsts = gst.objects.all()
    pproduct = get_object_or_404(Product, Product_Refrence_ID=pk)
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

    if request.method == 'POST':

        # try:
        #     excel_file = request.FILES['excel_file']
        #     file_name = excel_file.name
        #     product_ref_id = file_name.split('_')[-1].split('.')[0]
            
        #     if not excel_file.name.endswith('.xlsx'):
        #         messages.error(request, 'Invalid file format. Please upload a valid Excel file.')
        #         return redirect('pproductlist')
            
        #     with transaction.atomic():
        #         wb = load_workbook(excel_file)
        #         ws1 = wb['product_special_items']
        #         ws2 = wb['product_special_configs']
        #         Number_of_items = 0

        #         for row in ws1.iter_rows(min_row=2,min_col=1):
        #             product_sku = row[0]
        #             Number_of_items = Number_of_items + 1
                    
        #             for cell in row:
        #                 cell_value_item = cell.value   #get the cell value
        #                 column_letter = get_column_letter(cell.column)  # get the letter of that column 
        #                 if column_letter != 'A': 

        #                     found_rows = []
        #                     search_column = 'B'   # column with the locations
        #                     search_value = column_letter #column letter of that item from w1
        #                     for cell in ws2[search_column]: #search 
        #                         if cell.value == search_value: # if cell value in column B in ws2 == column of the item in ws1 

        #                             # If the condition is met, get the entire row's data
        #                             row_data = [cell.value for cell in ws2[cell.row]] # value of each cell in ws2[cell row number ex 5]

        #                             item_id = Item_Creation.objects.get(item_name=cell_value_item)
        #                             product_instance = PProduct_Creation.objects.get(PProduct_SKU=product_sku.value)
        #                             obj , created = set_prod_item_part_name.objects.get_or_create(id = row_data[0])
        #                             obj.location = row_data[1]
        #                             obj.part_name = row_data[2]
        #                             obj.part_dimentions = row_data[3] 
        #                             obj.dimention_total = row_data[4]
        #                             obj.part_pieces = row_data[5]
        #                             obj.part_type = row_data[6]
        #                             obj.save()
                                                              
        #                             obj1, created = product_2_item_through_table.objects.get_or_create(PProduct_pk =product_instance,Item_pk=item_id)
        #                             obj1.set_prod_config.add(obj.id)
        #                             obj1.save()
                         
                            
        # except Exception as e:
        #     messages.error(request, f'Error uploading Excel file: {str(e)}')

        form = PProductAddForm(request.POST, request.FILES, instance = pproduct) 
        formset = CustomPProductaddFormSet(request.POST, request.FILES , instance=pproduct)
        if form.is_valid() and formset.is_valid():
            form.save(commit=False)
            formset.save()
            
            #p_id has the id of the product
            p_id = form.instance
            print(p_id)
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
            return redirect('pproductlist')
        
        else:
            print(form.errors)
            print(formset.errors)
            return render(request, 'product/edit_production_product.html', {'gsts':gsts,
                                                                            'form':form,
                                                                            'formset':formset,
                                                                            'colors':colors,
                                                                            'products_sku_counts':products_sku_counts,
                                                                            'main_categories':main_categories,
                                                                            'prod_main_cat_name':prod_main_cat_name,
                                                                            'prod_main_cat_id':prod_main_cat_id,
                                                                            'prod_sub_cat_dict':prod_sub_cat_dict,
                                                                            'prod_sub_cat_dict_all':prod_sub_cat_dict_all})
    form = PProductAddForm(instance=pproduct)
    formset = CustomPProductaddFormSet(instance=pproduct)

    return render(request, 'product/edit_production_product.html',{'gsts':gsts,'form': form,'formset':formset,'colors':colors,
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
    
    queryset = Product.objects.select_related('Product_GST').prefetch_related('productdetails','productdetails__PProduct_color').all()
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
    print(request.POST)
    product = PProduct_Creation.objects.get(pk=pk)   #get the instance of the product
    formset = ProductVideoFormSet(instance= product)  # pass the instance to the formset
    if request.method == 'POST':
        formset = ProductVideoFormSet(request.POST, instance=product)
        
        if formset.is_valid():
            print(formset.deleted_forms)
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
    


def product2item(request,pk):
    print(request.POST)
    items = Item_Creation.objects.all()
    product_creation = PProduct_Creation.objects.get(pk=pk)   #get the instance of the product
    formset = Product2ItemFormset(instance= product_creation)  # pass the instance to the formset
    product_name = product_creation.Product.Model_Name
    product_color = product_creation.PProduct_color

    if request.method == 'POST':
        formset = Product2ItemFormset(request.POST, instance=product_creation)
        
        if formset.is_valid():           
            # when using form.save(commit=False) we need to  explicitly delete forms marked in has_deleted
            for form in formset.deleted_forms:
                if form.instance.pk:  # Ensure the form instance has a primary key before attempting deletion
                    form.instance.delete()

            for form in formset:
                if form not in formset.deleted_forms: # check if form not in deleted forms to avoid saving it again 
                    form.save(commit=False)
                    form.common_unique = False
                    form.save()
            messages.success(request,'Items to Product sucessfully added.')
            close_window_script = """
            <script>
            window.opener.location.reload(true);  // Reload parent window if needed
            window.close();  // Close current window
            </script>
            """
            return HttpResponse(close_window_script)

    else:
            return render(request, 'production/product2itemset.html', {'formset': formset, 'product': product_creation,
                                                                       'product_name':product_name,
                                                                       'product_color':product_color,'items':items})

    return render(request, 'production/product2itemset.html', {'formset': formset, 'product': product_creation,
                                                               'product_name':product_name,
                                                               'product_color':product_color,'items':items})

def product2commonitem(request,product_id):
    print(request.POST) 
    items = Item_Creation.objects.all()

    product = get_object_or_404(Product, Product_Refrence_ID=product_id) #get the product of the refrence id
    product_name = product.Model_Name
    
    product_instance = PProduct_Creation.objects.filter(Product=product).first()
    print('product',product)
    pproducts = PProduct_Creation.objects.filter(Product=product) #filter all instances related to the product


    # Fetch the queryset of product_2_item_through_table instances related to the filtered PProduct_Creation instances of a product ref id 
    # common_unique represents True if its common in all products and False it its unique to a product
    product_items_qs = product_2_item_through_table.objects.filter(PProduct_pk__in=pproducts).filter(common_unique=True)
    print('product_items_qs',product_items_qs)

    #instance and queryset params explained in file #formsets_for_accessing_reverse_relations.txt
    formset = Product2CommonItemFormSet(instance=product_instance,queryset=product_items_qs) # queryset of all the instannces of productcreation binded to form 
    print('formset_get',formset)


    if request.method == 'POST':
        formset = Product2CommonItemFormSet(request.POST, instance=product_instance, queryset=product_items_qs)

        if formset.is_valid():
            # when using form.save(commit=False) we need to  explicitly delete forms marked in has_deleted
            for form in formset.deleted_forms:
                if form.instance.pk:  # Ensure the form instance has a primary key before attempting deletion
                    form.instance.delete()

            for form in formset:
                if form not in formset.deleted_forms: # check if form not in deleted forms to avoid saving it again 
                    form.save(commit = False)
                    form.common_unique = True
                    form.save()

            messages.success(request,'Items to Product sucessfully added.')
            close_window_script = """
            <script>
            window.opener.location.reload(true);  // Reload parent window if needed
            window.close();  // Close current window
            </script>
            """
            return HttpResponse(close_window_script)
        
        else:
            return render(request, 'production/product2commonitemset.html', {'formset': formset,
                                                                       'product_name':product_name,
                                                                       'items':items})

    return render(request, 'production/product2commonitemset.html', {'formset': formset,
                                                               'product_name':product_name,
                                                               'items':items})




#____________________________Product-View-End__________________________________

#_____________________Item-Views-start_______________________

def item_create(request):
    title = 'Item Create'
    gsts = gst.objects.all()
    fab_grp = Fabric_Group_Model.objects.all()
    unit_name = Unit_Name_Create.objects.all()
    packaging_material_all = packaging.objects.all()
    fab_finishes = FabricFinishes.objects.all()
    print(request.POST)
    colors = Color.objects.all()

    
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES)
        
        if form.is_valid():
            form_instance = form.save()

            messages.success(request,'Item has been created, Update quantity in godown')
            return redirect(reverse('item-edit', args=[form_instance.id]))
        
        else:
            print(form.errors)
            return render(request,'product/item_create_update.html', {'gsts':gsts,
                                                                      'fab_grp':fab_grp,
                                                                      'unit_name':unit_name,
                                                                      'colors':colors,
                                                                      'packaging_material_all':packaging_material_all,
                                                                      'fab_finishes':fab_finishes,
                                                                      'title':title,'form':form})
    
    form = Itemform()
    return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
                                                                 'packaging_material_all':packaging_material_all,
                                                                    'fab_finishes':fab_finishes,
                                                                 'form':form})

# in request.get data is sent to server via url and it can be accessed using the name variable 
# which has ?namevaraible = data data from the querystring

# in request.POST u can access data sent to server with name varaible which has data from the
# name= as a key and value=  which has the value from the form
    
def item_list(request):
    g_search = request.GET.get('item_search')
    #select related for loading forward FK relationships and select related for reverse relationship  
    #annotate to make a temp table in item_creation for the sum of all item and its related shades in all godowns 
    queryset = Item_Creation.objects.select_related('Item_Color','unit_name_item',
                                                    'Fabric_Group',
                                                    'Item_Creation_GST','Item_Fabric_Finishes','Item_Packing').prefetch_related('shades','shades__godown_shades').all().annotate(total_quantity=Sum('shades__godown_shades__quantity'))


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
            print(formset)
            print('forms',formset.forms)
            formsethas_changed = [forms for forms in formset if formset.has_changed()]
            print('has_changed',formsethas_changed)
            form.save()
            formset.save()
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
    print(request.POST)

    godowns =  Godown_raw_material.objects.all()

    formset = None
    if parent_row_id is not None and primary_key is not None:
        shade_instance =  get_object_or_404(item_color_shade,pk=primary_key)
        formset = OpeningShadeFormSetupdate(request.POST or None, instance = shade_instance, prefix = "opening_shade_godown_quantity_set")

    elif primary_key is None and parent_row_id is not None:

        loaded_data = False
        #get data from session
        if 'openingquantitytemp' in request.session:
            session_quantity_data = request.session['openingquantitytemp']
            loaded_data = json.loads(session_quantity_data)

        
        if loaded_data:
            print('testtt')
            new_row_data = loaded_data.get('new_row', {})
            initial_data_backend = []

            count = 0 
            for key, value in new_row_data.items():
                initial_data_backend.append({
                        "opening_godown_id": int(value['gid']),
                        "opening_quantity": float(value['quantity']),
                        "opening_rate": float(loaded_data['all_rate'])})

                count = count + 1

            total_forms = len(initial_data_backend)
            opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_rate','opening_quantity','opening_godown_id'], extra=total_forms)            
            formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),initial=initial_data_backend,prefix = "opening_shade_godown_quantity_set")
            print(formset.forms)
        else:
            opening_shade_godown_quantitycreateformset = modelformset_factory(opening_shade_godown_quantity, fields = ['opening_rate','opening_quantity','opening_godown_id'], extra=1)            
            formset = opening_shade_godown_quantitycreateformset(queryset=opening_shade_godown_quantity.objects.none(),prefix = "opening_shade_godown_quantity_set")
    
    if request.method == 'POST':
        if primary_key is not None:
            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        form.save()

        else:

            total_forms = int(request.POST.get('opening_shade_godown_quantity_set-TOTAL_FORMS'))
            all_rate = request.POST.get('opening_shade_godown_quantity_set-0-opening_rate')
            
            new_row = {}
            for form_prefix_id in range(total_forms):
                
                godown_id =  f"opening_shade_godown_quantity_set-{form_prefix_id}-opening_godown_id"
                quantity =  f"opening_shade_godown_quantity_set-{form_prefix_id}-opening_quantity"

                difference_quantity =  f"opening_shade_godown_quantity_set-{form_prefix_id}-old_opening_quantity"

                godown_id_get = request.POST.get(godown_id)
                quantity = request.POST.get(quantity)
                difference_quantity_get = request.POST.get(difference_quantity)

                new_row[f'row_{form_prefix_id}'] = {'gid':godown_id_get,'quantity':quantity,"updateqty":difference_quantity_get} 

            data_to_store = {'parent_row_prefix_id': parent_row_id, 'all_rate':all_rate, 'new_row':new_row}
            # Convert the data to JSON string
            
            data_json_string = json.dumps(data_to_store)
            
            # Store the JSON string in the session
            request.session['openingquantitytemp'] = data_json_string


    return render(request,'product/opening_godown_qty.html',{'formset':formset,'godowns':godowns })




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
    return JsonResponse('test')

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
                messages.success(request, 'Color created successfully.')
                return HttpResponse('<script>window.close();</script>') 
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
                return HttpResponse('<script>window.close();</script>')

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
                return HttpResponse('<script>window.close();</script>')

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



def ledgercreate(request):
    print(request.POST)
    current_date = now().date()
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
            else:
                print(form.errors)
            messages.success(request,'Ledger Created')
            return redirect('ledger-list')
        
        else:
            
            return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create','current_date':current_date})
    

    return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Create','current_date':current_date})
    


def ledgerupdate(request,pk):
    under_groups = AccountSubGroup.objects.all()
    current_date = now().date()
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
        print(request.POST)
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
            
            return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Update','current_date':current_date , 'open_bal':opening_balance})
    
    return render(request,'accounts/ledger_create_update.html',{'form':form,'under_groups':under_groups,'title':'ledger Update','current_date':current_date, 'open_bal':opening_balance})



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
                                            godown_instance.purchase_voucher_godown_item = items_instance #save form to permanant table with link to parent table 
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

            formset = purchase_voucher_items_godown_formset(popup_godown_data, instance = voucher_item_instance,prefix='shade_godown_items_set')
            
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
        print('TESTT',godowns_for_selected_shade)
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

    print('popupurl', popup_url)
    return JsonResponse({'popup_url':popup_url})





def purchasevoucheritemsearchajax(request):
    try:
        # Retrieve the partial name typed by the user from the GET request
        item_name_typed = request.GET.get('nameValue')
        if not item_name_typed:
            raise ValidationError("No partial name provided.")

        item_name_searched = Item_Creation.objects.filter(item_name__icontains=item_name_typed)

        if item_name_searched:
            # Prepare a dictionary of searched items with IDs as keys and names as values
            searched_item_name_dict = {queryset.id: queryset.item_name for queryset in item_name_searched}

            """
            or 
            searched_item_name_dict = {}
            for queryset in item_name_searched:
                item_name = queryset.item_name
                item_id = queryset.id
                searched_item_name_dict[item_id] = item_name

            """
            return JsonResponse({'item_name_typed': item_name_typed, 'searched_item_name_dict': searched_item_name_dict})
        else:
            return JsonResponse({'error': 'No items found.'}, status=404)

    except ValidationError as ve:
        error_message = str(ve)
        return JsonResponse({'error': error_message}, status=400)
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return JsonResponse({'error': error_message}, status=500)
    

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

    print(f'gstupdate/{pk}')
    print(request.path)
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
                return HttpResponse('<script>window.close();</script>')
        else:
            messages.success(request,'An error occured.')

    return render(request,template_name,{'form' : form, 'title':title,'gsts':gsts})




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
                return HttpResponse('<script>window.close();</script>')
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
                return HttpResponse('<script>window.close();</script>')
        else:
            messages.error(request, 'An error accoured.')  

    return render(request, template_name ,{'form':form,'title':title,'packaging_all':packaging_all})





def packaging_delete(request,pk):
    packaging_pk =  packaging.objects.get(pk=pk)
    packaging_pk.delete()
    messages.success(request,'Packing deleted.')
    return redirect('packaging-create-list')



#__________________________Sub Category End_____________________________



#_________________________production-end______________________________

def set_production_popup(request,p_name,p_reference_id):
    context = {'product_name':p_name,'product_ref_id':p_reference_id}

    if request.method == 'POST':
        return HttpResponse('<script>window.close();</script>')
    
    return render(request,'production/set_production.html', context=context)



# def set_production_upload(request,product_ref_id,item_number):
#     number_of_items = int(item_number)
#     product_products = PProduct_Creation.objects.filter(Product__Product_Refrence_ID=product_ref_id)

#     #check if product has any set productions
#     product_2_items_exists = product_2_item_through_table.objects.filter(PProduct_pk__Product__Product_Refrence_ID=product_ref_id).first()

#     workbook = Workbook()
    
#     #delete the default workbook
#     default_sheet = workbook['Sheet']
#     workbook.remove(default_sheet)

#     workbook.create_sheet('product_special_items')
#     workbook.create_sheet('product_special_configs')
#     workbook.create_sheet('product_common_items')
#     workbook.create_sheet('product_common_configs')
    
#     sheet1 = workbook.worksheets[0]
#     sheet2 = workbook.worksheets[1]
#     sheet3 = workbook.worksheets[2]
#     sheet4 = workbook.worksheets[3]

#     # wb1 product_sku
#     firstcell = sheet1.cell(row=1, column=1)
#     firstcell.value = "product_sku"
#     sheet1.column_dimensions['A'].width = 30  # Adjust the width as needed

#     #for entering the products
#     col_num = 2
#     for products in product_products:
#         product_sku = products.PProduct_SKU
#         sheet1[f'A{col_num}'] = product_sku
#         col_num = col_num + 1


#     #for creating columns for fabric group
#     row_num = 1
#     for row in sheet1.iter_rows(min_row=1, max_row=1, min_col=2, max_col = number_of_items + 1):
#         for cell in row:
#             cell.value = f"fabric_{row_num}"

#             # Set the width of the current column (function to get the column letter from cell)
#             col_letter = get_column_letter(cell.column)
#             sheet1.column_dimensions[col_letter].width = 20  # Adjust the width
#             row_num = row_num + 1


#     #unlock the editable part of the sheet 
#     for row in sheet1.iter_rows(min_row=2, max_row = len(product_products) + 1 ,min_col=2, max_col= number_of_items + 1):
#         for cell in row:
#             cell.protection = Protection(locked =False)

#         if product_2_items_exists:
#             pass

#     # wb2
#     for row in sheet2.iter_rows(min_row=1, max_row=1, min_col=1, max_col=7):
#         row[0].value = 'id'
#         row[1].value = 'location'
#         row[2].value = 'name'
#         row[3].value = 'calculation'
#         row[4].value = 'total'
#         row[5].value = 'cut_part'
#         row[6].value = 'type'
        

#         #get the column letter of the above and change the width 
#         for cell in row:
#             column_letter = get_column_letter(cell.column)
#             sheet2.column_dimensions[column_letter].width = 20

#     #unlock the editable part of the sheet
#     for col in sheet2.iter_cols(min_row=2,max_row=10000,min_col=2, max_col=7):    
#         for cell in col:
#             cell.protection = Protection(locked = False)

#     # Protect the entire worksheet
#     sheet1.protection.sheet = True
#     sheet2.protection.sheet = True
    

#     fileoutput = BytesIO()
#     workbook.save(fileoutput)
    
#     # Prepare the HTTP response with the Excel file content
#     response = HttpResponse(fileoutput.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     file_name_with_pk = f'product_reference_id_{product_ref_id}'
#     response['Content-Disposition'] = f'attachment; filename="{file_name_with_pk}.xlsx"'

#     return response




#_________________________production-send______________________________

#__________________________reports-start_________________________________

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
    return render(request, 'product/login.html', context=context)



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
