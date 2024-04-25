from django.contrib.auth.models import User , Group
from uuid import UUID
import json
from django.contrib.auth.models import auth #help us to logout
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from . models import (AccountGroup, AccountSubGroup, Color, Fabric_Group_Model,
                       FabricFinishes, Godown_finished_goods, Godown_raw_material,
                         Item_Creation, Ledger, MainCategory, PProduct_Creation, Product,
                           Product2SubCategory,  ProductImage, RawStockTransfer, StockItem,
                             SubCategory, Unit_Name_Create, account_credit_debit_master_table,
                               gst, item_color_shade, item_godown_quantity_through_table,
                                 item_purchase_voucher_master, packaging, purchase_voucher_items, shade_godown_items,
                                   shade_godown_items_temporary_table)
from .forms import(ColorForm, CreateUserForm, CustomPProductaddFormSet,
                    FabricFinishes_form, ItemFabricGroup, Itemform, LedgerForm,
                     LoginForm, OpeningShadeFormSet, PProductAddForm, PProductCreateForm, ShadeFormSet,
                       StockItemForm, UnitName, account_sub_grp_form, PProductaddFormSet,
                        ProductImagesFormSet, ProductVideoFormSet,
                         gst_form, item_purchase_voucher_master_form,
                           packaging_form, product_main_category_form, 
                            product_sub_category_form, purchase_voucher_items_formset,
                             purchase_voucher_items_godown_formset, purchase_voucher_items_formset_update,
                                shade_godown_items_temporary_table_formset,shade_godown_items_temporary_table_formset_update)
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.utils.timezone import now
from django.contrib import messages



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

    print(request.POST)
    if request.method == 'POST':
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
    formset = ProductVideoFormSet(instance=product)  # pass the instance to the formset
    if request.method == 'POST':
        formset = ProductVideoFormSet(request.POST, instance=product)
        print(formset)
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

    colors = Color.objects.all()

    
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES)
        
        if form.is_valid():
            #make a var of saved form and get the id 
            instance = form.save()
            messages.success(request,'Item has been created, Update quantity in godown')
            return redirect(reverse('item-edit', args=[instance.id]))
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
    queryset = Item_Creation.objects.select_related('Item_Color','unit_name_item',
                                                    'Fabric_Group',
                                                    'Item_Creation_GST').prefetch_related('shades').all()


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

    openingquantityformset = OpeningShadeFormSet()
    
    # when in item_edit the item is edited u can also edit or add shades to it which also gets updated or added
    # as item_edit instance is also provided while updating or adding with formsets to the shades module
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES , instance=item_pk)
        formset = ShadeFormSet(request.POST , request.FILES, instance=item_pk)
        
        if form.is_valid() and formset.is_valid():
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



def item_delete(request, pk):
    
    try:
        item_pk = get_object_or_404(Item_Creation,pk = pk)
        item_pk.delete()
        messages.success(request,f'Item {item_pk.item_name} was deleted')
    except IntegrityError as e:
        messages.error(request, f'Cannot delete {item_pk.item_name} because it is referenced by other objects.')
    return redirect('item-list')


#_____________________Item-Views-end_______________________

#_____________________Color-start________________________



def color_create_update(request, pk=None):
    if request.path == '/simple_colorcreate_list/':
        template_name = 'product/color_list.html'
        title = 'Color List'

    elif request.path == '/simple_colorcreate_update/':
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
            if 'save_and_add_another' in request.POST:
                messages.success(request, 'Color created successfully.')
                return redirect('simplecolorlist')
            
            elif 'save' in request.POST and request.path == '/simple_colorcreate_update/':
                if instance:
                    messages.success(request, 'Color updated successfully.')
                else:
                    messages.success(request, 'Color created successfully.')
                return redirect('simplecolorlistonly')
            
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
    return redirect('simplecolorlistonly')

def colorpopup(request):
    return render(request,'product/color_popup.html')

# def color_create(request):
#     if request.method == 'POST':
#         form = ColorForm(request.POST)
#         if form.is_valid():
#             form.save()
#             if 'save_and_add_another' in request.POST:
#                 form = ColorForm()
#                 return render(request,'product/create_color.html',{'form': form, 'return_url_get': request.session.get('return_url_color', '/')})
#             #get the return url from the session and redirect it to the same 
#             return_url = request.session.get('return_url_color', '/')
#             # delete the session
#             del request.session['return_url_color']
#             return redirect(return_url)
#         else:
#             print(form.errors)
#             return render(request,"product/create_color.html",{'form': form})
#     else:
#         #store HTTP_REFERER which has the previous page route in the session 
#         if 'return_url_color' not in request.session:
#             return_url_get = request.META.get('HTTP_REFERER', '/')
#             request.session['return_url_color'] = return_url_get
#         form = ColorForm()
#         return render(request,'product/create_color.html',{'form': form, 'return_url_get': request.session.get('return_url_color', '/')})



#_____________________Color-end________________________



#_______________________fabric group start___________________________________

# def item_fabric_group_create(request):
#     form = ItemFabricGroup()
#     if request.method == 'POST':
#         form = ItemFabricGroup(request.POST)
#         if form.is_valid():
#             form.save()
#             #get the return url from the session and redirect it to the same 
#             return_url = request.session.get('return_url', '/')
#             # delete the session
#             del request.session['return_url']
#             return redirect(return_url)
#         else:
#             return render(request,'product/item_fabric_group_create_update.html',{'title': 'Create Fabric Group','form':form})
#     else:
#         return_url_get = request.META.get('HTTP_REFERER', '/')
#         request.session['return_url'] = return_url_get
#         return render(request,'product/item_fabric_group_create_update.html',{'title': 'Create Fabric Group','form':form,'return_url_get':return_url_get})


def item_fabric_group_create(request):
    form = ItemFabricGroup()
    
    if request.path == '/itemfabricgroupcreate/':
        template_name = 'product/item_fabric_group_create_update.html'

    elif request.path == '/fabric_popup/':
        template_name = 'product/fabric_popup.html'


    if request.method == 'POST':
        form = ItemFabricGroup(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Fabric group created.')
            if 'save_and_add_another' in request.POST and template_name == 'product/item_fabric_group_create_update.html':
                
                return redirect('item-fabgroup-create')
            
            elif 'save' in request.POST and template_name == 'product/item_fabric_group_create_update.html':

                return redirect('item-fabgroup-list')

            elif 'save' in request.POST and template_name == 'product/fabric_popup.html':

                return HttpResponse('<script>window.close();</script>')

        else:
            print(form.errors)
            return render(request,template_name,{'title': 'Create Fabric Group',
                                                                                  'form':form})


    return render(request,template_name,{'title': 'Create Fabric Group',
                                                                          'form':form})


def item_fabric_group_list(request):
    fab_group_all = Fabric_Group_Model.objects.all()
    return render(request,'product/fabric_group_list.html', {"fab_group_all":fab_group_all})


def item_fabric_group_update(request,pk):
    item_fabric_pk =  get_object_or_404(Fabric_Group_Model,pk=pk)
    form = ItemFabricGroup(instance = item_fabric_pk)
    if request.method == 'POST':
        form = ItemFabricGroup(request.POST,instance = item_fabric_pk)
        if form.is_valid():
            form.save()
            messages.success(request,'Fabric group updated.')
            return redirect('item-fabgroup-list')
        else:
            
            return render(request,'product/item_fabric_group_create_update.html',{'title': 'Update Fabric Group',
                                                                                  'form':form})
    else:
        return render(request,'product/item_fabric_group_create_update.html',{'title': 'Update Fabric Group',
                                                                              'form':form})


def item_fabric_group_delete(request,pk):
    try:
        item_fabric_pk = get_object_or_404(Fabric_Group_Model,pk=pk)
        item_fabric_pk.delete()
        messages.success(request,f'Fabric group {item_fabric_pk.fab_grp_name} was deleted')

    except IntegrityError as e:
        messages.error(request,f'Cannot delete {item_fabric_pk.fab_grp_name} because it is referenced by other objects.')
    
    return redirect('item-fabgroup-list')


def fabricpopup(request):
    return render(request,'product/fabric_popup.html')
#_______________________fabric group end___________________________________

#_______________________Unit Name Start____________________________________

def unit_name_create(request):
    print(request.POST)
    form = UnitName()
    if request.path == '/unitnamecreate/':
        template_name = 'product/unit_name_create_update.html'

    elif request.path == '/units_popup/':
        template_name = 'product/units_popup.html'

    if request.method == 'POST':
        form = UnitName(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Unit created sucessfully.')

            if 'save_and_add_another' in request.POST and template_name == 'product/unit_name_create_update.html':
        
                return redirect('unit_name-create')
            
            elif 'save' in request.POST and template_name == 'product/unit_name_create_update.html':

                return redirect('unit_name-list')

            elif 'save' in request.POST and template_name == 'product/units_popup.html':
                return HttpResponse('<script>window.close();</script>')

        else:
            print(form.errors)
            return render(request, template_name, {'title': 'Create Unit','form':form})
        
    else:
        return render(request, template_name, {'title':'Create Unit','form':form})


def unit_name_list(request):
    unit_name_all = Unit_Name_Create.objects.all()
    return render(request,'product/unit_name_list.html', {"unit_name_all":unit_name_all})


def unit_name_update(request,pk):
    unit_name_pk = get_object_or_404(Unit_Name_Create,pk=pk)
    form = UnitName(instance=unit_name_pk)
    if request.method == 'POST':
        form = UnitName(request.POST ,instance=unit_name_pk)
        if form.is_valid():
            form.save()
            messages.success(request,'Unit updated.')
            return redirect('unit_name-list')
        else:
            return render(request, 'product/unit_name_create_update.html', {'title':'Update Unit' ,
                                                                            "form":form})
    return render(request, 'product/unit_name_create_update.html', {'title':'Update Unit' ,
                                                                    "form":form})



def unit_name_delete(request,pk):
    try:
        unit_name_pk = get_object_or_404(Unit_Name_Create,pk=pk)
        unit_name_pk.delete()
        messages.success(request,f'Unit name {unit_name_pk.unit_name} was deleted.')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {unit_name_pk.unit_name} because it is referenced by other objects.')
    return redirect('unit_name-list')


def unitnamepopup(request):
    return render(request,'product/units_popup.html')
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



def stock_item_create(request):
    print(request.POST)
    accsubgrps = AccountSubGroup.objects.all()
    form = StockItemForm()
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock item created sucessfully')
            if 'save' in request.POST:
                return redirect('stock_item-list')
            elif 'save_and_add_another' in request.POST:
                return redirect('stock-item-create')
        else:
            print(form.errors)
            return render(request,'product/stock_item_create_update.html', {'title':'Stock Item Create',
                                                                            'accsubgrps':accsubgrps,
                                                                            'form':form})
    
    
    return render(request,'product/stock_item_create_update.html', {'title':'Stock Item Create',
                                                                    'accsubgrps':accsubgrps,
                                                                    'form':form})



def stock_item_update(request, pk):

    accsubgrps = AccountSubGroup.objects.all()
    stock =get_object_or_404(StockItem ,pk=pk)
    form = StockItemForm(instance = stock)
    if request.method == 'POST':
        form = StockItemForm(request.POST, instance = stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock item updated sucessfully')
            return redirect('stock_item-list')
        else:
            print(form.errors)
            return render(request, 'product/stock_item_create_update.html', {'title':'Stock Item Update',
                                                                             'accsubgrps':accsubgrps,
                                                                             'form':form})
    return render(request, 'product/stock_item_create_update.html', {'title':'Stock Item Update',
                                                                     'accsubgrps':accsubgrps,
                                                                     'form':form})


def stock_item_list(request):

    stocks = StockItem.objects.all()
    return render(request,'product/stock_item_list.html', {"stocks":stocks})


def stock_item_delete(request, pk):
    try:
        stock = get_object_or_404(StockItem ,pk=pk)
        stock.delete()
        messages.success(request,f'Stock Item {stock.stock_item_name} was deleted')
    except IntegrityError as e:
        messages.error(request,f'Cannot delete {stock.stock_item_name} because it is referenced by other objects.')        
    return redirect('stock_item-list')



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
            name_value = form.cleaned_data['name']
            debit_credit_value = form.cleaned_data['Debit_Credit']

            if debit_credit_value == 'Debit':
                account_credit_debit_master_table.objects.create(ledger = ledger_instance, account_name= name_value,voucher_type = 'Ledger' ,debit= open_bal_value)

            elif debit_credit_value == 'Credit':
                account_credit_debit_master_table.objects.create(ledger = ledger_instance, account_name= name_value,voucher_type = 'Ledger',credit= open_bal_value)
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
    if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
        print('Master_post',request.POST)

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
        
        items = Item_Creation.objects.all()

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
        try:
            with transaction.atomic(): #start a database transaction
                #create a form instance for main form
                master_form = item_purchase_voucher_master_form(request.POST,instance=purchase_invoice_instance)

                #create a formset instance for form items in invoice
                items_formset = item_formsets_change

                #create a formset instance for godowns in form items
                godown_items_formset = purchase_voucher_items_godown_formset(request.POST, prefix='shade_godown_items_set')

                #filter out only the forms which are changed or added 
                items_formset.forms = [form for form in items_formset.forms if form.has_changed()]  
            
                if master_form.is_valid() and items_formset.is_valid():
                    # Save the master form
                    master_instance = master_form.save()
                
                    # Check for items marked for deletion and delete them 
                    # delete wont work after default as we are not saving items_formset instead we are saving  in the formsets individually
                    # items_formset.deleted_forms has the forms marked for deletion
                    for form in items_formset.deleted_forms:
                        if form.instance.pk:
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
                                unique_id = request.POST.get(f'item_unique_id_{form_prefix_number}')
                                primary_key = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-id')

                                #check if pk is not there in the formset which means form is newly created then its been saved in temp godown with unique id 
                                if primary_key == '' or primary_key == None: 
                                    purchase_voucher_temp_data = shade_godown_items_temporary_table.objects.filter(unique_id=unique_id)
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
                                            godown_instance.purchase_voucher_godown_item = items_instance
                                            godown_instance.save()
                                            saved_data_to_delete = saved_data_to_delete + 1
                                            print('Data-saved')
                                        else:
                                            print('godown',godown_form.error)
                                            purchase_voucher_temp_data.delete()

                                    # godown_item_json = request.POST.get('jsonData')
                                    # print('godown_item_json',godown_item_json)
                                    # item_shade = request.POST.get(f'purchase_voucher_items_set-{godown_item_json.parent_row_prefix_id}-item_shade')
                                    # print('item_shade',item_shade)

                                    if saved_data_to_delete == form_set_id:
                                        purchase_voucher_temp_data.delete()
                                
                                # first check if quantity is updated in invoice database 
                                godown_item_quantity = request.POST.get(f'purchase_voucher_items_set-{form_prefix_number}-jsonDataInputquantity')

                                voucher_row_godown_data = json.loads(godown_item_quantity)
                                parent_row_prefix_id = voucher_row_godown_data.get('parent_row_prefix_id')

                                if parent_row_prefix_id == form_prefix_number:
                                    print(voucher_row_godown_data)
                                    new_row = voucher_row_godown_data.get('newRow')
                                    new_rate = float(voucher_row_godown_data.get('all_Rate'))
                                    row_item = items_instance.item_shade.id
                                    Item_instance =  item_color_shade.objects.get(id = row_item)
                                    for key, value in new_row.items():
                                        godown_id = int(value['gId'])
                                        qtydiffrence = value['updateQty']
                                        godown_instance = Godown_raw_material.objects.get(id = godown_id)
                                        Item, created = item_godown_quantity_through_table.objects.get_or_create(godown_name = godown_instance,Item_shade_name = Item_instance)
                                        Item.quantity = Item.quantity + qtydiffrence
                                        Item.item_rate = new_rate
                                        Item.save()
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
            print('an error occoured-',e)
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
               'items':items,
               'items_formset':items_formset,
               'Purchase_gst':Purchase_gst,
               'godown_formsets':godown_items_formset,
               'item_godowns_raw':raw_material_godowns,
               }

    return render(request,'accounts/purchase_invoice.html',context=context)


#popup page for purchase voucher godown update
#url for this func is generated by purchasevouchercreategodownpopupurl func 
def purchasevoucherpopup(request,shade_id,prefix_id,unique_id=None,pk=None):
    
    #unique_id generation is on add button so created rows will not have unique id
    # create dynamic formsets depends on create or update 

    if unique_id is not None:
        #filter the instances by the unique_id which acts as temp primarykey for invoiceitems table
        temp_instances = shade_godown_items_temporary_table.objects.filter(unique_id=unique_id)
        
        if temp_instances:
            formsets = shade_godown_items_temporary_table_formset_update(request.POST or None, queryset = temp_instances,prefix='shade_godown_items_set')

        else:
            formsets = shade_godown_items_temporary_table_formset(request.POST or None, queryset = temp_instances,prefix='shade_godown_items_set')
    

    elif pk is not None:
        voucher_item_instance = purchase_voucher_items.objects.get(id=pk)

        formsets = purchase_voucher_items_godown_formset(request.POST or None, instance = voucher_item_instance,prefix='shade_godown_items_set')
    
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
                                                                 'errors': formset.errors,'prefix_id':prefix_id}
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
                'unique_id': unique_id, 'shade_id': shade_id, 'errors': formset.errors,'prefix_id':prefix_id
            }
            return render(request, 'accounts/purchase_popup.html', context)
    return render(request, 'accounts/purchase_popup.html' ,{'godowns':godowns,'item':item,
                                                            'item_shade':item_shade,'formset':formset,
                                                            'unique_id':unique_id,'prefix_id':prefix_id})


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



def purchasevoucherlist(request):
    purchase_invoice_list = item_purchase_voucher_master.objects.all()
    return render(request,'accounts/purchase_invoice_list.html',{'purchase_invoice_list':purchase_invoice_list})


def purchasevoucherdelete(request,pk):
    purchase_invoice_pk = get_object_or_404(item_purchase_voucher_master,pk=pk)
    purchase_invoice_pk.delete()
    return redirect('purchase-voucher-list')
                    

def session_data_test(request):
    temp_data_exists = None
    if 'temp_data_exists' in request.session: 
        temp_data_exists = request.session['temp_data_exists']
    temp_uuid = None
    if 'temp_uuid' in request.session:
        temp_uuid = request.session['temp_uuid']

    context = {'temp_data_exists':temp_data_exists , 'temp_uuid':temp_uuid}
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
    if pk:
        instance = gst.objects.get(pk=pk)
        title = 'Update'

    else:
        instance = None
        title = 'Create'

    print(request.path)
    if request.path == '/gstpopup/':
        template_name = 'accounts/gst_popup.html'
    
    
    elif request.path == '/gstcreate/':
        template_name = 'accounts/gst_create_update.html'

    
    form = gst_form(instance = instance)
    if request.method == 'POST':
        form = gst_form(request.POST, instance = instance)
        if form.is_valid():
            form.save()

            messages.success(request,'GST created successfully.')
            if 'save_and_add_another' in request.POST and template_name == 'accounts/gst_create_update.html':
                return redirect('gst-create')
            
            elif 'save' in request.POST and template_name == 'accounts/gst_create_update.html':
                return redirect('gst-list')

            elif 'save' in request.POST and template_name == 'accounts/gst_popup.html':
                return HttpResponse('<script>window.close();</script>')
        else:
            messages.success(request,'An error occured.')

    return render(request,template_name,{'form' : form, 'title':title})


def gst_list(request):
    gsts =  gst.objects.all()
    return render(request,'accounts/gst_list.html',{'gsts':gsts})



def gst_delete(request,pk):
    gst_pk = gst.objects.get(pk=pk)
    gst_pk.delete()
    messages.success(request,'GST deleted')
    return redirect('gst-list')



def fabric_finishes_create_update(request, pk = None):
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
            messages.success(request,'fabric finish created')
            if 'save_and_add_another' in request.POST and template_name == 'misc/fabric_finishes_create_update.html':
                return redirect('fabric-finishes-create')
    
            elif 'save' in request.POST and template_name == 'misc/fabric_finishes_create_update.html':
                return redirect('fabric-finishes-list')
            
            elif 'save' in request.POST and template_name == 'misc/fabric_finishes_popup.html':
                return HttpResponse('<script>window.close();</script>')
        else:
            messages.error(request,'An error occured.')

    return render(request,template_name,{'form':form,'title':title})




def fabric_finishes_list(request):
    fabricfinishes =  FabricFinishes.objects.all()
    return render(request,'misc/fabric_finishes_list.html',{'fabricfinishes':fabricfinishes})



def fabric_finishes_delete(request,pk):
    fabric_finish =  FabricFinishes.objects.get(pk=pk)
    fabric_finish.delete()
    messages.success(request,'fabric finish deleted.')
    return redirect('fabric-finishes-list')


def packaging_create_update(request, pk = None):
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
            messages.success(request,'packing created.')

            if 'save_and_add_another' in request.POST and template_name == 'misc/packaging_create_update.html':
                return redirect('packaging-create')
            
            elif 'save' in request.POST and template_name == 'misc/packaging_create_update.html':
                return redirect('packaging-list')

            elif 'save' in request.POST and template_name == 'misc/packaging_popup.html':
                return HttpResponse('<script>window.close();</script>')
        else:
            messages.error(request, 'An error accoured.')  

    return render(request, template_name ,{'form':form,'title':title})




def packaging_list(request):
    packaging_all =  packaging.objects.all()
    return render(request,'misc/packaging_list.html',{'packaging_all':packaging_all})



def packaging_delete(request,pk):
    packaging_pk =  packaging.objects.get(pk=pk)
    packaging_pk.delete()
    messages.success(request,'Packing deleted.')
    return redirect('packaging-list')



#__________________________Sub Category End_____________________________




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


# def index(request):
#     return render(request,"product/index.html")


# def listproduct(request):
#     queryset = Product.objects.all()
#     product_image = ProductImage.objects.filter(Image_ID=1)
#     context = {'products' : queryset, 'image': product_image}
#     for image in product_image:
#         print(image.Image.url)
#     return render(request, 'product/list_products.html', context)


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



# def deleteproduct(request, pk):
#     product = Product.objects.get(id = pk)
#     product.delete()
#     print('record deleted')
#     return redirect('listproduct')


# def aplus(request):
#     return render(request, 'product/aplus.html')




