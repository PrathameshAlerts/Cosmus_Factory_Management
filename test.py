def product_color_sku(request):
    color = Color.objects.all()
    
    if request.method == 'POST':
           
        # OR Product_ref_id = request.POST['Product_Refrence_ID']
            product_ref_id = request.POST.get('Product_Refrence_ID')
            
            
            # Flag to check if all sets of fields are valid
            all_sets_valid = False
            for i in range(1, 5):  #Assuming up to 5 sets of fields
                # Build field names dynamically
                image_field_name = f'PProduct_image_{i}'
                color_field_name = f'PProduct_color_{i}'
                sku_field_name = f'PProduct_SKU_{i}'
                print('FILES= ', request.FILES)
                print('POST= ',request.POST)
                # Create a dictionary with the dynamic field names
                data = {
                    'PProduct_image': request.FILES.get(image_field_name),
                    'PProduct_color': request.POST.get(color_field_name),
                    'PProduct_SKU': request.POST.get(sku_field_name),
                    'Product_Refrence_ID': product_ref_id
                }
                print("data=", data)
                # Create a form instance for the current set of fields
                current_form = PProductCreateForm(data,request.FILES)
                
                
                # Save the form if it is valid
                if current_form.is_valid():
                        print("cleaned_data=",current_form.cleaned_data)
                        all_sets_valid = True
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
                        current_form.save()
                        
                    

                else:
                    if current_form.errors:
                        print(current_form.errors)
                        
                    return render(request,'product/product_color_sku.html',{'form':current_form,'color':color})
                    
            #Redirect to the detail view of the created instance with id 
            if all_sets_valid:
                return redirect(reverse('edit_production_product', args=[product_ref_id]))
    else:
        form = PProductCreateForm()
    return render(request, 'product/product_color_sku.html', {'form':form,'color':color})