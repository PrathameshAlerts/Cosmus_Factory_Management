from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse
from . models import Color, Fabric_Group_Model, Item_Creation, PProduct_Creation, Product , ProductImage, Unit_Name_Create
from .forms import ColorForm, CreateUserForm, ItemFabricGroup, Itemform, LoginForm, PProductAddForm, ProductForm , EditProductForm ,PProductCreateForm, UnitName
from django.urls import reverse
from django.contrib.auth.models import User , Group
from django.contrib.auth.models import auth #help us to logout
from django.contrib.auth import  update_session_auth_hash ,authenticate # help us to authenticate users
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction

def index(request):
    return render(request,"product/index.html")


def listproduct(request):
    queryset = Product.objects.all()
    product_image = ProductImage.objects.filter(Image_ID=1)
    context = {'products' : queryset, 'image': product_image}
    for image in product_image:
        print(image.Image.url)
    return render(request, 'product/list_products.html', context)


def add_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES) 
        print(request.POST)
        print(request.FILES)
        if form.is_valid():
            # product = Product(
            #     # reference_image=request.FILES.get('reference_image'),
            #     Product_Name=form.cleaned_data['Product_Name'],
            #     Model_Name=form.cleaned_data['Model_Name'],
            #     Product_Status=form.cleaned_data['Product_Status'],
            #     Product_Channel = form.cleaned_data['Product_Channel'],
            #     Product_SKU = form.cleaned_data['Product_SKU'],
            #     Product_HSNCode =  form.cleaned_data['Product_HSNCode'],
            #     Product_WarrantyTime = form.cleaned_data['Product_WarrantyTime'],
            #     Product_MRP =  form.cleaned_data['Product_MRP'],
            #     Product_SalePrice_CustomerPrice =  form.cleaned_data['Product_SalePrice_CustomerPrice'],
            #     Product_BulkPrice = form.cleaned_data['Product_BulkPrice'],
            #     Product_Cost_price = form.cleaned_data['Product_Cost_price']
            #)
            # product.save()
            #or
            product = form.save(commit=False)
            product.images = ProductImage.objects.create(Image=request.FILES['Image'])
            form.save()
            return redirect('listproduct')

    else:
        return render(request, 'product/add_product.html', {'form':form})
    return render(request, 'product/add_product.html',{'form': form})



def edit_product(request, pk):
    product = Product.objects.get(id = pk)
    form = EditProductForm(instance=product)

    if request.method == "POST":
        form = EditProductForm(request.POST, instance=product) # request.POST has the data from the form and instance has the data from the database
        if form.is_valid():
            form.save() # saves the product changes in the database

            # handles images
            #request.POST has data sent by the form in key value pair 
            #where key corresponds to the name = field in the form and value is the actual data
            for i in range(1,11): # as we have 10 images to upload
                image_type = request.POST.get(f'Image_type_{i}')
                order_by =  request.POST.get(f'Order_by_{i}')
                image_file = request.FILES.get(f'Image_{i}')  
                #Product=product (product = Product.objects.get(id = pk)), Image_ID=i,: These are the conditions for
                #finding an existing ProductImage instance. It looks for an instance where the 
                #associated product is the given product and the Image_ID is equal to i. 
                #defaults={'Image': image_file, 'Image_type': image_type, 'Order_by': order_by}: 
                #If no matching instance is found, this dictionary specifies the default values 
                #to use when creating a new instance. It sets the image file (Image), image type 
                #(Image_type), and order (Order_by) with the values obtained from the form.
                
                if image_file:
                    #ProductImage.objects.get_or_create(: This is a manager method 
                    #(objects is the default manager for a Django model) that interacts with the database.
                    #Get or create an image 
                    product_image, created = ProductImage.objects.get_or_create(
                        Product = product, Image_ID = i,
                        defaults = {'Image':image_file, 'Image_type':image_type, 'Order_by': order_by}
                    )

                    if not created:
                        #update the existing product
                        product_image.Image = image_file
                        product_image.Image_type = image_type
                        product_image.Order_by = order_by
                        product_image.save()
            return redirect('listproduct')
    context = {'form': form, 'product': product}
    return render(request, 'product/edit_product.html', context)



def deleteproduct(request, pk):
    product = Product.objects.get(id = pk)
    product.delete()
    print('record deleted')
    return redirect('listproduct')


def aplus(request):
    return render(request, 'product/aplus.html')


#____________________________Production-Product-View-Start__________________________________

def dashboard(request):
    return render(request,'product/dashboard.html')



def edit_production_product(request,pk):
    pproduct = Product.objects.get(Product_Refrence_ID=pk)
    form = PProductAddForm(instance=pproduct)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=pproduct) 
        if form.is_valid():
            form.save()
            return redirect('pproductlist')
    else:
        print(form.errors)
        return render(request, 'product/edit_production_product.html', {'form':form})
    return render(request, 'product/edit_production_product.html',{'form': form})


#transaction.atomic
def product_color_sku(request):
    print(request.POST)
    color = Color.objects.all()
    if request.method == 'POST':
        product_ref_id = request.POST.get('Product_Refrence_ID')
        
        with transaction.atomic():
            all_sets_valid = False
            try:
                for i in range(1, 5): 
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
                        print(current_form.errors)
                        all_sets_valid = False
                        #explicitly set transaction to rollback on errors
                        transaction.set_rollback(True)
                        break
                    
            except Exception as e:
                print('Exception occured', str(e))

        
        if all_sets_valid:

            # reverse is used to generate a url with both the arguments, which then redirect can use to redirect
            return redirect(reverse('edit_production_product', args=[product_ref_id]))
        else:
                # Return a response with errors for invalid sets of fields
                return render(request, 'product/product_color_sku.html', {'form':current_form,'color': color})

    else:
        form = PProductCreateForm()
        return render(request, 'product/product_color_sku.html', {'form': form, 'color': color})




def pproduct_list(request):
    queryset = Product.objects.all()
    product_search = request.GET.get('product_search')

    if product_search != '' and product_search is not None:
        queryset = Product.objects.filter(Q(Product_Name__icontains=product_search)|
                                            Q(Model_Name__icontains=product_search)|
                                            Q(Product_Refrence_ID__icontains=product_search)|
                                            Q(productdetails__PProduct_SKU__icontains=product_search)).distinct()
    print(queryset)
    context = {'products': queryset}
    return render(request,'product/pproduct_list.html',context=context)



def pproduct_delete(request, pk):
    product = Product.objects.get(Product_Refrence_ID=pk)
    product.delete()
    return redirect('pproductlist')


#____________________________Product-View-End__________________________________

#_____________________Item-Views-start_______________________

def item_create(request):
    print(request.POST)
    if request.method == 'POST':
        form = Itemform(request.POST, request.FILES)
        if form.is_valid():
            
            form.save()
            return render(request,'product/success.html')
        else:
            return render(request,'product/create_item.html', {'form':form})
    else:
        form = Itemform()
       
        return render(request, 'product/create_item.html', {'form':form})


# in request.get data is sent to server via url and it can be accessed using the name variable 
# which has ?namevaraible = data data from the querystring

# in request.POST u can access data sent to server with name varaible which has data from the
# value= atribite in the form
    
def item_list(request):
    g_search = request.GET.get('item_search')
    queryset = Item_Creation.objects.all()
    
    print(request.GET)
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
    item_pk = Item_Creation.objects.get(pk = pk)
    form = Itemform(instance = item_pk)
    if request.method == 'POST':
        form = Itemform(request.POST, instance=item_pk)
        if form.is_valid():
            form.save()
            return redirect('item-list')
        else:
            return render(request,'product/edit_item.html',{'form':form})
    else:
        return render(request,'product/edit_item.html',{'form':form})


def item_delete(request, pk):
    item_pk = Item_Creation.objects.get(pk = pk)
    item_pk.delete()
    return redirect('item-list')


#_____________________Item-Views-end_______________________


#_____________________Color-start________________________



# def color_list(request):
#     color = Color.objects.all()
#     context = {'colors':color}
#     return render(request,'product/list_color.html', context=context)



def color_create(request, pk=None):
    color = Color.objects.all()
    template_name = "product/create_color.html"


    if pk:
        instance = get_object_or_404(Color, pk = pk)
    else:
        instance = None

    form = ColorForm(instance=instance)
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()

            if 'save_and_add_another' in request.POST:
                return redirect('colorlist')
            
            return redirect('item-create')
        else:
            print(form.errors)
            return render(request, template_name ,{'form': form, 'colors':color})


    return render(request, template_name ,{'form': form, 'colors':color})
        

def color_delete(request, pk):
    product_color = Color.objects.get(pk=pk)
    product_color.delete()
    return redirect('colorlist')



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




# def color_edit(request,pk):
#     colors = Color.objects.get(pk = pk)
#     form = ColorForm(instance=colors)
#     print(colors)
#     if request.method == "POST":
#         form = ColorForm(request.POST,instance = colors)
#         print(form)
#         if form.is_valid():
#             form.save()
#             return redirect('colorlist')
#         else:
#             return render(request, 'product/color_edit.html', {"form":form})
#     else:
#         return render(request, 'product/color_edit.html', {"form":form})





#_____________________Color-end________________________



#_______________________fabric group start___________________________________

def item_fabric_group_create(request):
    form = ItemFabricGroup()
    if request.method == 'POST':
        form = ItemFabricGroup(request.POST)
        if form.is_valid():
            form.save()
            #get the return url from the session and redirect it to the same 
            return_url = request.session.get('return_url', '/')
            # delete the session
            del request.session['return_url']
            return redirect(return_url)
        else:
            return render(request,'product/item_fabric_group_create.html',{'form':form})
    else:
        return_url_get = request.META.get('HTTP_REFERER', '/')
        request.session['return_url'] = return_url_get
        return render(request,'product/item_fabric_group_create.html',{'form':form,'return_url_get':return_url_get})


def item_fabric_group_list(request):
    fab_group_all = Fabric_Group_Model.objects.all()
    return render(request,'product/fabric_group_list.html', {"fab_group_all":fab_group_all})


def item_fabric_group_update(request,pk):
    item_fabric_pk = Fabric_Group_Model.objects.get(pk=pk)
    form = ItemFabricGroup(instance = item_fabric_pk)
    if request.method == 'POST':
        form = ItemFabricGroup(request.POST,instance = item_fabric_pk)
        if form.is_valid():
            form.save()
            return redirect('item-fabgroup-list')
        else:
            return render(request,'product/fabric_group_update.html',{'form':form})
    else:
        return render(request,'product/fabric_group_update.html',{'form':form})


def item_fabric_group_delete(request,pk):
    item_fabric_pk = Fabric_Group_Model.objects.get(pk=pk)
    item_fabric_pk.delete()
    return redirect('item-fabgroup-list')

#_______________________fabric group end___________________________________

#_______________________Unit Name Start____________________________________

def unit_name_create(request):
    form = UnitName()
    if request.method == 'POST':
        form = UnitName(request.POST)
        if form.is_valid():
            form.save()
            return redirect('unit_name-list')
        else:
            return render(request, "product/unit_name_create.html", {'form':form})
    else:
        return render(request, "product/unit_name_create.html", {'form':form})



def unit_name_list(request):
    unit_name_all = Unit_Name_Create.objects.all()
    return render(request,'product/unit_name_list.html', {"unit_name_all":unit_name_all})


def unit_name_update(request,pk):
    unit_name_pk = Unit_Name_Create.objects.get(pk=pk)
    form = UnitName(instance=unit_name_pk)
    if request.method == 'POST':
        form = UnitName(request.POST ,instance=unit_name_pk)
        if form.is_valid():
            form.save()
            return redirect('unit_name-list')
        else:
            return render(request, 'product/unit_name_update.html', {"form":form})
    return render(request, 'product/unit_name_update.html', {"form":form})



def unit_name_delete(request,pk):
    unit_name_pk = Unit_Name_Create.objects.get(pk=pk)
    unit_name_pk.delete()
    return redirect('unit_name-list')



#________________________Unit Name End_______________________________________







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








