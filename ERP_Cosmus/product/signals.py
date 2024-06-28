
from django.db.models.signals import pre_delete , post_save,pre_save
from django.dispatch import receiver
from .models import Ledger, PProduct_Creation, Product, RawStockTrasferRecords, account_credit_debit_master_table, item_purchase_voucher_master, item_godown_quantity_through_table,Item_Creation,item_color_shade, opening_shade_godown_quantity, product_2_item_through_table, purchase_order, purchase_order_to_product, purchase_voucher_items, set_prod_item_part_name, shade_godown_items
import logging

logger = logging.getLogger('product_signals')


#post_save signal for item_color_shade if Item_Creation instance is created 
@receiver(post_save, sender=Item_Creation)
def save_primary_item_color_shade(sender, instance, created, **kwargs): #instance is the created instance of Item_Creation
# data in the instance is from the form which is submitted in the front end 
    if created:

        #getting the color name attribte instead of object
        color_name = instance.Item_Color.color_name  #  color_name is in str representation in color model or else it will give obj of 
        
        logger.info(f"Item Shade of color- {color_name} -created")
        # Create a new item_color_shade object related to the newly created instance
        primary_color_shade = item_color_shade.objects.create(items=instance,  # Assign the instance itself, not just the primary key
                                                            item_name_rank= 1,
                                                            item_shade_name = color_name,
                                                            item_color_image = instance.item_shade_image)
        # Save the newly created item_color_shade object
        primary_color_shade.save()



#signal to reduce the quantity from all the godowns in the invoice if it was deleted and delete it form c/d master table
@receiver(pre_delete, sender=item_purchase_voucher_master)
def handle_invoice_delete(sender, instance, **kwargs):
    invoice_item_instance = instance.purchase_voucher_items_set.all() # invoice_item_instance carried the deleted instance data before deleting
    
    for items in invoice_item_instance:
        item_shade = items.item_shade
        item_godowns_instance = items.shade_godown_items_set.all()

        for g_items in  item_godowns_instance:
            godown = g_items.godown_id
            quantity = g_items.quantity
            godown_quantity_to_delete = item_godown_quantity_through_table.objects.get(godown_name=godown,Item_shade_name=item_shade)  # godown_quantity_to_delete carries the already present quantity in the table
            logger.info(f"quantity reduced from c/d table after Invoice Delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
            godown_quantity_to_delete.quantity = godown_quantity_to_delete.quantity - quantity
            godown_quantity_to_delete.save()
            

    # delete instance form c/d master if entire invoice is deleted
    purchase_voucher = instance.purchase_number
    instance_get = account_credit_debit_master_table.objects.get(voucher_no = purchase_voucher)        
    instance_get.delete()



#signal to reduce the quantity from all the godowns in the invoiceitem was deleted 
@receiver(pre_delete, sender=purchase_voucher_items)
def handle_invoice_items_delete(sender, instance, **kwargs):
    
    #check if instance was deleted directly or via models.CASCADE
    if instance.deleted_directly:
        invoice_godown_items_instance = instance.shade_godown_items_set.all()
        item_shade = instance.item_shade
        for g_items in invoice_godown_items_instance:            
            godown = g_items.godown_id
            quantity = g_items.quantity
            godown_quantity_to_delete = item_godown_quantity_through_table.objects.get(godown_name=godown,Item_shade_name=item_shade)
            logger.info(f"quantity reduced from c/d table after Invoice Items Delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
            godown_quantity_to_delete.quantity = godown_quantity_to_delete.quantity - quantity
            godown_quantity_to_delete.save()
            

#signal to reduce the quantity from the godowns in the godown in the itemrow was deleted 
@receiver(pre_delete, sender=shade_godown_items)
def handle_invoice_items_godowns_delete(sender, instance, **kwargs):
    
    #check if instance was deleted directly or via models.CASCADE
    if instance.deleted_directly:
        godown = instance.godown_id
        quantity = instance.quantity

        #get the extra attribute created in purchasevoucherpopupupdate() to get the old_shade and reduce the quantity.
        old_item_shade = getattr(instance, 'extra_data_old_shade', None)
        if old_item_shade is not None:
            item_shade = old_item_shade
        else:
            item_shade = instance.purchase_voucher_godown_item.item_shade
        
        godown_quantity_to_delete = item_godown_quantity_through_table.objects.get(godown_name=godown,Item_shade_name=item_shade)
        logger.info(f"quantity reduced from c/d table after Invoice Items godown delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
        godown_quantity_to_delete.quantity = godown_quantity_to_delete.quantity - quantity
        godown_quantity_to_delete.save()
        


@receiver(post_save, sender=item_purchase_voucher_master)
def save_purchase_invoice_report(sender, instance, created, **kwargs):
    purchase_voucher = instance.purchase_number
    purchase_ledger = instance.party_name
    ledger_type = instance.ledger_type
    grand_total = instance.grand_total
    
    
    if created:
        instance_create = account_credit_debit_master_table.objects.create(voucher_no = purchase_voucher,ledger=purchase_ledger,voucher_type = ledger_type, particulars= 'Raw Material', debit = grand_total, credit = 0)
        logger.info(f"Purchase Voucher Created with purchase voucher no - {purchase_voucher}, ledger no - {purchase_ledger.name}, Total - {grand_total}")
        instance_create.save()
    
    elif not created:
        instance_get = account_credit_debit_master_table.objects.get(voucher_no = purchase_voucher)
        logger.info(f"Purchase Voucher Updated with purchase voucher no - {purchase_voucher}, ledger no - {purchase_ledger.name}, Total - {grand_total}")
        instance_get.ledger=purchase_ledger
        instance_get.voucher_type = ledger_type
        instance_get.particulars = 'Raw Material'
        instance_get.debit = grand_total
        instance_get.credit = 0
        instance_get.save()
    

# signal to delete record from item_godown_quantity_through_table if qty = 0 after saving the record in the table 
@receiver(post_save, sender=item_godown_quantity_through_table)
def delete_item_godown_quantity_if_0(sender, instance, created, **kwargs):
    
    if not created:  #FIXME remove this if statement if 0 quantity values are creating issue on creating new model instances
        quantity_after_save = instance.quantity
        if quantity_after_save == 0:
            logger.info(f"Item Godown quantity instance deleted as quantity is 0, id - {instance.id}, - {instance.godown_name.godown_name_raw}, - {instance.Item_shade_name.item_shade_name}")
            instance.delete()



# signal for opening godown items in item create update 
@receiver(post_save, sender= opening_shade_godown_quantity)
def created_updated_opening_item_godown(sender, instance, created, **kwargs):

    new_opening_godown = instance.opening_godown_id
    opening_rate = instance.opening_rate
    item_shade_id = instance.opening_purchase_voucher_godown_item.id
    
    item_shade_instance = item_color_shade.objects.get(id = item_shade_id)

    opening_quantity_created = False
    opening_quantity_updated = False

    # if opening godown item instance created
    if created:
        opening_quantity_created = True
        opening_quantity = instance.opening_quantity



    # if opening godown item instance updated 
    elif not created:
        opening_quantity_updated = True
        old_opening_quantity = getattr(instance, 'old_opening_g_quantity', None)

        if old_opening_quantity is not None:
            opening_quantity_diffrence = instance.opening_quantity - old_opening_quantity
        


    # if created 
    if opening_quantity_created:
        obj, created = item_godown_quantity_through_table.objects.get_or_create(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
        if created:
            obj.quantity = opening_quantity
            obj.item_rate = opening_rate
            obj.save()

        else:
            obj.item_rate = opening_rate
            obj.quantity = obj.quantity + opening_quantity
            obj.save()


    # if updated 
    if opening_quantity_updated:
        old_opening_godown_id = getattr(instance, 'old_opening_godown_id', None) # old godown id to check if godown has changed or not 
        

        if old_opening_godown_id:
            
            # if godown has not changed 
            if old_opening_godown_id == new_opening_godown:

                # get Item2godown instance with instance godown and item shade 
                get_obj = item_godown_quantity_through_table.objects.get(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + opening_quantity_diffrence # add the diffrence_quantity to the quantity
                get_obj.save()



            # if godown has changed but quantities are same 
            elif old_opening_godown_id != new_opening_godown and instance.opening_quantity == old_opening_quantity:
                
                # decrease the qty
                # get Item2godown instance with old_gid and item shade
                decrease_obj_q = item_godown_quantity_through_table.objects.get(godown_name=old_opening_godown_id,Item_shade_name=item_shade_instance)
                decrease_obj_q.item_rate = opening_rate
                decrease_obj_q.quantity = decrease_obj_q.quantity - instance.opening_quantity # decrease the instance quantity from the quantity
                decrease_obj_q.save()

                # increase the qty 
                # get Item2godown instance with new_gid and item shade
                get_obj , created = item_godown_quantity_through_table.objects.get_or_create(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + instance.opening_quantity # increase the instance quantity from the quantity
                get_obj.save()
        


            # if godown has changed and also the quantities
            elif old_opening_godown_id != new_opening_godown and instance.opening_quantity != old_opening_quantity:
                
                # decrease the quantity 
                # get Item2godown instance with old_gid and decrease the quantity in respect to old quantity
                decrease_obj_q = item_godown_quantity_through_table.objects.get(godown_name=old_opening_godown_id, Item_shade_name=item_shade_instance)
                decrease_obj_q.item_rate = opening_rate
                decrease_obj_q.quantity = decrease_obj_q.quantity - old_opening_quantity
                decrease_obj_q.save()

                # get Item2godown instance with new_gid and increase the quantity in respect to new quantity
                get_obj , created = item_godown_quantity_through_table.objects.get_or_create(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + instance.opening_quantity
                get_obj.save()




# decrese quantity from item_godown_quantity_through_table if opening_shade_godown_quantity instance is deleted 
@receiver(pre_delete, sender= opening_shade_godown_quantity)
def handle_opening_godown_deleted(sender, instance, **kwargs):
    item_id = instance.opening_purchase_voucher_godown_item.id
    godown_id = instance.opening_godown_id
    quantity = instance.opening_quantity

    try:
        godown_item_through = item_godown_quantity_through_table.objects.get(Item_shade_name = item_id,godown_name = godown_id)

        if godown_item_through:
            godown_item_through.quantity = godown_item_through.quantity - quantity
            godown_item_through.save()

    except item_godown_quantity_through_table.DoesNotExist:
        # Log a message if the entry does not exist
        logger.error(f"No item_godown_quantity_through_table entry found for item_id {item_id} and godown_id {godown_id}")
        print(f"No item_godown_quantity_through_table entry found for item_id {item_id} and godown_id {godown_id}")

    except Exception as e:
        # Log any other exceptions that occur
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        


#for stock transfer
@receiver(post_save, sender=RawStockTrasferRecords)
def created_updated_raw_stock_trasfer(sender, instance, created, **kwargs):

    source_godown_value = instance.master_instance.source_godown
    destination_godown_value = instance.master_instance.destination_godown

    if created:
        item_shade = instance.item_shade_transfer
        item_quantity = instance.item_quantity_transfer

        item_to_godown_quantity_through_source = item_godown_quantity_through_table.objects.get(godown_name=source_godown_value,Item_shade_name=item_shade)
        item_to_godown_quantity_through_source.quantity = item_to_godown_quantity_through_source.quantity - item_quantity
        item_to_godown_quantity_through_source.save()


        item_to_godown_quantity_through_destination, created = item_godown_quantity_through_table.objects.get_or_create(godown_name=destination_godown_value,Item_shade_name=item_shade)

        if created:
            item_to_godown_quantity_through_destination.quantity = item_quantity
            item_to_godown_quantity_through_destination.save()

        else:
            item_to_godown_quantity_through_destination.quantity = item_to_godown_quantity_through_destination.quantity + item_quantity
            item_to_godown_quantity_through_destination.save()
    
    
    if not created:
        pass
        




@receiver(post_save, sender=purchase_order)
def created_updated_purchase_order_product_qty(sender, instance, created, **kwargs):
    purchase_order_instance = instance
    product_id = instance.product_reference_number

    if created:
        products = Product.objects.get(Product_Refrence_ID=product_id.Product_Refrence_ID)

        for product in products.productdetails.all():
            purchase_order_to_product.objects.create(purchase_order_id=purchase_order_instance,product_id=product,order_quantity=0)


    if not created:
        products = PProduct_Creation.objects.filter(Product = product_id)
        
        for product in products:
            obj, created = purchase_order_to_product.objects.get_or_create(purchase_order_id=purchase_order_instance,product_id=product)




# signal to set latest rate of an item after purchase invoice
@receiver(post_save, sender=purchase_voucher_items)
def set_item_rate_on_purchase(sender, instance, created, **kwargs):
    item_rate = instance.rate
    item_id = instance.item_shade.items.id

    if item_id:
        item_instance = Item_Creation.objects.get(id=item_id)
        item_instance.rate = item_rate
        item_instance.save()



# signal to set latest rate of an item after opening godown quantity added
@receiver(post_save, sender=opening_shade_godown_quantity)
def set_item_rate_on_purchase(sender, instance, created, **kwargs):
    item_rate = instance.opening_rate
    item_id = instance.opening_purchase_voucher_godown_item.items.id

    if item_id:
        item_instance = Item_Creation.objects.get(id=item_id)  # set item rate only if the rate is 0, which means there is no purchase made. 
        if item_instance.rate == 0:
            item_instance.rate = item_rate
            item_instance.save()














# @receiver(pre_save, sender=Item_Creation)
# def update_combined_field(sender, instance, **kwargs):
#     # Combine the values of field1 and field2 and save it to combined_field
#     instance.Description = f"{instance.Fabric_Group} - {instance.Name} - {instance.Item_Color}"


"""
        or in forms
            def clean(self):
        cleaned_data = super().clean()
        # Get values from the three fields
        value1 = cleaned_data.get('field1')
        value2 = cleaned_data.get('field2')
        value3 = cleaned_data.get('field3')

        # Perform logic to autofill the autofill_field
        if value1 and value2 and value3:
            autofill_value = f'{value1}-{value2}-{value3}'
            cleaned_data['autofill_field'] = autofill_value

        return cleaned_data
"""