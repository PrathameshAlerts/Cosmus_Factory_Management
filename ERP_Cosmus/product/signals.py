from django.db.models.signals import pre_delete , post_save
from django.dispatch import receiver
from .models import Ledger, account_credit_debit_master_table, item_purchase_voucher_master, item_godown_quantity_through_table,Item_Creation,item_color_shade, purchase_voucher_items, shade_godown_items



#post_save signal for item_color_shade if Item_Creation instance is created 
@receiver(post_save, sender=Item_Creation)
def save_primary_item_color_shade(sender, instance, created, **kwargs): #instance is the created instance of Item_Creation
# data in the instance is from the form which is submitted in the front end 
    if created:
        #getting the color name attribte instead of object function
        color_name = instance.Item_Color.color_name  #  color_name is in str representation in color model or else it will give obj of color
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
    invoice_item_instance = instance.purchase_voucher_items_set.all()
    
    for items in invoice_item_instance:
        item_shade = items.item_shade
        item_godowns_instance = items.shade_godown_items_set.all()

        for g_items in  item_godowns_instance:
            godown = g_items.godown_id
            quantity = g_items.quantity
            godown_quantity_to_delete = item_godown_quantity_through_table.objects.get(godown_name=godown,Item_shade_name=item_shade)
            godown_quantity_to_delete.quantity = godown_quantity_to_delete.quantity - quantity
            godown_quantity_to_delete.save()
            

    # delete instance form c/d master if entire invoice is deleted
    purchase_voucher = instance.purchase_number
    instance_get = account_credit_debit_master_table.objects.get(voucher_no = purchase_voucher)        
    instance_get.delete()


# if 'using' not in kwargs: this check is done to make sure that the deleting request has come directly from delete() and not from
# models.CASCADE 'using' is set in Kwargs when instance is deleted as a result of models.CASCADE
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
        godown_quantity_to_delete.quantity = godown_quantity_to_delete.quantity - quantity
        godown_quantity_to_delete.save()
        


@receiver(post_save, sender=item_purchase_voucher_master)
def save_purchase_invoice_report(sender, instance, created, **kwargs):
    purchase_voucher = instance.purchase_number
    purchase_ledger = instance.party_name
    ledger_type = instance.ledger_type
    grand_total = instance.grand_total
    
    
    if created:
        instance_create = account_credit_debit_master_table.objects.create(voucher_no = purchase_voucher,ledger=purchase_ledger,voucher_type = ledger_type, particulars= 'Raw Material',debit = grand_total,credit = 0)
        instance_create.save()
    
    elif not created:
        instance_get = account_credit_debit_master_table.objects.get(voucher_no = purchase_voucher)
        instance_get.ledger=purchase_ledger
        instance_get.voucher_type = ledger_type
        instance_get.particulars = 'Raw Material'
        instance_get.debit = grand_total
        instance_get.credit = 0
        instance_get.save()
    

# signal to delete  0 quantity on update of model instance 
@receiver(post_save, sender=item_godown_quantity_through_table)
def delete_item_godown_quantity_if_0(sender, instance, created, **kwargs):
    if not created:  # remove this if statement if 0 quantity values are creating issue on creating new model instances
        quantity_after_save = instance.quantity
        if quantity_after_save == 0:
            instance.delete()




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