
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from . models import AccountGroup, AccountSubGroup, Color, Fabric_Group_Model, Godown_finished_goods,  Godown_raw_material, Item_Creation, Ledger, PProduct_Creation, Product , ProductImage, RawStockTransfer, StockItem, Unit_Name_Create, account_credit_debit_master_table, gst, item_color_shade, item_godown_quantity_through_table
from .forms import ColorForm, CreateUserForm, CustomPProductaddFormSet, ItemFabricGroup, Itemform, LedgerForm, LoginForm, PProductAddForm, PProductCreateForm, ShadeFormSet, StockItemForm, UnitName, account_sub_grp_form, PProductaddFormSet
from django.urls import reverse
from django.contrib.auth.models import User , Group
from django.contrib.auth.models import auth #help us to logout
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import get_object_or_404



#____________________________Production-Product-View-Start__________________________________

def dashboard(request):
    return render(request,'misc/dashboard.html')



def edit_production_product(request,pk):
    gsts = gst.objects.all()
    pproduct = get_object_or_404(Product, Product_Refrence_ID=pk)

    if request.method == 'POST':
        form = PProductAddForm(request.POST, request.FILES, instance = pproduct) 
        formset = CustomPProductaddFormSet(request.POST, request.FILES , instance=pproduct)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('pproductlist')
        else:
            print(form.errors)
            return render(request, 'product/edit_production_product.html', {'gsts':gsts,
                                                                            'form':form,
                                                                            'formset':formset})
    form = PProductAddForm(instance=pproduct)
    formset = CustomPProductaddFormSet(instance=pproduct)
    return render(request, 'product/edit_production_product.html',{'gsts':gsts,'form': form,'formset':formset})


def product_color_sku(request):
    color = Color.objects.all()
    print(request.POST)
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

                        # Create a dictionary with the dynamic field names
                        data = {
                            'PProduct_color': request.POST.get(color_field_name),
                            'PProduct_SKU': request.POST.get(sku_field_name),
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
    return render(request, 'product/product_color_sku.html', {'form': form, 'color': color})


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


#____________________________Product-View-End__________________________________

#_____________________Item-Views-start_______________________

def item_create(request):
    title = 'Item Create'
    gsts = gst.objects.all()
    fab_grp = Fabric_Group_Model.objects.all()
    unit_name = Unit_Name_Create.objects.all()
    colors = Color.objects.all()

    print(request.POST, request.FILES)
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request,'Item has been created')
            return redirect("item-list")
        else:
            print(form.errors)
            return render(request,'product/item_create_update.html', {'gsts':gsts,
                                                                      'fab_grp':fab_grp,
                                                                      'unit_name':unit_name,
                                                                      'colors':colors,
                                                                      'title':title,'form':form})
    
    form = Itemform()
    return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
                                                                 'form':form})

# in request.get data is sent to server via url and it can be accessed using the name variable 
# which has ?namevaraible = data data from the querystring

# in request.POST u can access data sent to server with name varaible which has data from the
# value= atribite in the form
    
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
    item_pk = get_object_or_404(Item_Creation,pk = pk)

    form = Itemform(instance = item_pk)
    formset = ShadeFormSet(instance= item_pk)

    # when in item_edit the item is edited u can also edit or add shades to it which also gets updated or added
    # as item_edit instance is also provided while updating or adding with formsets to the shades module
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES , instance=item_pk)
        formset = ShadeFormSet(request.POST , request.FILES, instance=item_pk)
        if form.is_valid() and formset.is_valid():
            print(formset.cleaned_data)
            form.save()
            formset.save()
            messages.success(request,'Item updated successfully')
            return redirect('item-list')
        else:

            return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                     'fab_grp':fab_grp,
                                                                     'unit_name':unit_name,
                                                                     'colors':colors,
                                                                     'title':title,
                                                                     'form':form,
                                                                     'formset': formset})
    else:
        return render(request,'product/item_create_update.html',{'gsts':gsts,
                                                                 'fab_grp':fab_grp,
                                                                 'unit_name':unit_name,
                                                                 'colors':colors,
                                                                 'title':title,
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

    else:
        template_name = "product/create_color_modal.html"
        title = 'Colors'
    
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
            
            elif 'save' in request.POST:
                if instance:
                    messages.success(request, 'Color updated successfully.')
                else:
                    messages.success(request, 'Color created successfully.')
                return redirect('simplecolorlistonly')
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
    print(request.POST)
    if request.method == 'POST':
        form = ItemFabricGroup(request.POST)
        if form.is_valid():
            form.save()
            if 'save_and_add_another' in request.POST:
                messages.success(request,'Fabric group created.')
                return redirect('item-fabgroup-create')
            
            elif 'save' in request.POST:
                messages.success(request,'Fabric group created.')
                return redirect('item-fabgroup-list')
        else:
            print(form.errors)
            return render(request,'product/item_fabric_group_create_update.html',{'title': 'Create Fabric Group',
                                                                                  'form':form})


    return render(request,'product/item_fabric_group_create_update.html',{'title': 'Create Fabric Group',
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

#_______________________fabric group end___________________________________

#_______________________Unit Name Start____________________________________

def unit_name_create(request):
    form = UnitName()
    if request.method == 'POST':
        form = UnitName(request.POST)
        if form.is_valid():
            form.save()

            if 'save_and_add_another' in request.POST:
                messages.success(request,'Unit created sucessfully.')
                return redirect('unit_name-create')
            
            elif 'save' in request.POST:
                messages.success(request,'Fabric group created sucessfully.')
                return redirect('unit_name-list')
        
        else:
            return render(request, "product/unit_name_create_update.html", {'title': 'Create Unit','form':form})
    else:
        return render(request, "product/unit_name_create_update.html", {'title':'Create Unit','form':form})


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
            return redirect('account_sub_group-list')
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
            return redirect('stock_item-list')
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
        print(request.POST)
        godown_name =  request.POST['godown_name']
        godown_type = request.POST['Godown_types']
        if godown_type == 'Raw Material':
            godown_raw = Godown_raw_material(godown_name_raw=godown_name)
            godown_raw.save()
            messages.success(request,'Raw material godown created.')
            return redirect('godown-list')
        
        elif godown_type == 'Finished Goods':
            godown_finished = Godown_finished_goods(godown_name_finished=godown_name)
            godown_finished.save()
            messages.success(request,'Finished goods godown created.')
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
        item_create_table = item_color_shade.objects.filter(items=item_name_value)

        item_shades = {}
        #loop in the throughtable with the selected shade of the selected item   
        for x in item_create_table:

            # in the through table to with the selected shade of the selected item and selected godown
            shades_of_item_in_selected_godown = item_godown_quantity_through_table.objects.filter(godown_name = item_color_godown, Item_shade_name=x.id)

            # loop through the filtered queryset of shades in the godown and make 
            # item_shade dict to send in front end 
            for x in shades_of_item_in_selected_godown:
                shade_name = x.Item_shade_name.item_shade_name
                shade_id = x.Item_shade_name.id
                item_shades[shade_id] = shade_name


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
                                'item_color':item_color,'item_per':item_per, 'shade_quantity':shade_quantity })
        

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

def purchasevouchercreate(request):
    return render(request,'.html')



def purchasevoucherupdate(request,pk):
    return render(request,'.html')



def purchasevoucherlist(request):
    return render(request,'.html')


def purchasevoucherdelete(request,pk):
    pass



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




