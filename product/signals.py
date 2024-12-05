
from django.db.models.signals import pre_delete , post_save,pre_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.core.exceptions import ValidationError , ObjectDoesNotExist
from .models import (Finished_goods_transfer_records, Ledger, PProduct_Creation, Product, Product_warehouse_quantity_through_table, RawStockTrasferRecords,
                      account_credit_debit_master_table, godown_item_report_for_cutting_room,  item_purchase_voucher_master, 
                      item_godown_quantity_through_table,Item_Creation,item_color_shade, labour_workout_master, 
                      opening_shade_godown_quantity, product_2_item_through_table, product_godown_quantity_through_table, product_purchase_voucher_items, purchase_order, purchase_order_for_raw_material, purchase_order_for_raw_material_cutting_items, purchase_order_raw_material_cutting,
                        purchase_order_to_product, purchase_order_to_product_cutting, purchase_voucher_items, set_prod_item_part_name,
                          shade_godown_items)


import logging

logger = logging.getLogger('product_signals')



@receiver(post_save, sender=Item_Creation)
def save_primary_item_color_shade(sender, instance, created, **kwargs): 

    if created:

        
        color_name = instance.Item_Color.color_name  
        
        logger.info(f"Item Shade of color- {color_name}-created")
        
        primary_color_shade = item_color_shade.objects.create(items=instance,  
                                                            item_name_rank= 1,
                                                            c_user = instance.c_user,
                                                            item_shade_name = color_name,
                                                            item_color_image = instance.item_shade_image)
        
        primary_color_shade.save()




@receiver(pre_delete, sender=item_purchase_voucher_master)
def handle_invoice_delete(sender, instance, **kwargs):
    invoice_item_instance = instance.purchase_voucher_items_set.all() 
    
    for items in invoice_item_instance:
        item_shade = items.item_shade
        item_godowns_instance = items.shade_godown_items_set.all()

        for g_items in  item_godowns_instance:
            godown = g_items.godown_id
            quantity = g_items.quantity
            
            godown_quantity_to_delete, created = item_godown_quantity_through_table.objects.get_or_create(godown_name=godown,Item_shade_name=item_shade)  
            
            logger.info(f"quantity reduced from c/d table after Invoice Delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
            
            if created:
                qty_to_deduct = 0
            else:
                qty_to_deduct =  godown_quantity_to_delete.quantity

            godown_quantity_to_delete.quantity = qty_to_deduct - quantity
            godown_quantity_to_delete.save()
            

    
    purchase_voucher = instance.purchase_number
    instance_get = account_credit_debit_master_table.objects.get(voucher_no = purchase_voucher)        
    instance_get.delete()




@receiver(pre_delete, sender=purchase_voucher_items)
def handle_invoice_items_delete(sender, instance, **kwargs):
    
    
    if instance.deleted_directly:
        invoice_godown_items_instance = instance.shade_godown_items_set.all()
        item_shade = instance.item_shade
        for g_items in invoice_godown_items_instance:            
            godown = g_items.godown_id
            quantity = g_items.quantity
            godown_quantity_to_delete, created = item_godown_quantity_through_table.objects.get_or_create(godown_name=godown,Item_shade_name=item_shade)
            
            logger.info(f"quantity reduced from c/d table after Invoice Items Delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
            
            if created:
                qty_to_deduct = 0

            else:
                qty_to_deduct = godown_quantity_to_delete.quantity

            godown_quantity_to_delete.quantity = qty_to_deduct - quantity

            godown_quantity_to_delete.save()
            


@receiver(pre_delete, sender=shade_godown_items)
def handle_invoice_items_godowns_delete(sender, instance, **kwargs):
    
    
    if instance.deleted_directly:
        godown = instance.godown_id
        quantity = instance.quantity

        
        old_item_shade = getattr(instance, 'extra_data_old_shade', None)
        if old_item_shade is not None:
            item_shade = old_item_shade
        else:
            item_shade = instance.purchase_voucher_godown_item.item_shade
        
        godown_quantity_to_delete, created = item_godown_quantity_through_table.objects.get_or_create(godown_name=godown,Item_shade_name=item_shade)
        logger.info(f"quantity reduced from c/d table after Invoice Items godown delete -- id - {godown_quantity_to_delete.id} - quantity -  {quantity}")
        
        if created:
            qty_to_deduct = 0
        else:
            qty_to_deduct = godown_quantity_to_delete.quantity
        godown_quantity_to_delete.quantity = qty_to_deduct - quantity
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
    


@receiver(post_save, sender=item_godown_quantity_through_table)
def delete_item_godown_quantity_if_0(sender, instance, created, **kwargs):
    
    if not created:  
        quantity_after_save = instance.quantity
        if quantity_after_save == 0:
            logger.info(f"Item Godown quantity instance deleted as quantity is 0, id - {instance.id}, - {instance.godown_name.godown_name_raw}, - {instance.Item_shade_name.item_shade_name}")
            instance.delete()




@receiver(post_save, sender= opening_shade_godown_quantity)
def created_updated_opening_item_godown(sender, instance, created, **kwargs):

    new_opening_godown = instance.opening_godown_id
    opening_rate = instance.opening_rate
    item_shade_id = instance.opening_purchase_voucher_godown_item.id
    
    item_shade_instance = item_color_shade.objects.get(id = item_shade_id)

    opening_quantity_created = False
    opening_quantity_updated = False

    
    if created:
        opening_quantity_created = True
        opening_quantity = instance.opening_quantity



    
    elif not created:
        opening_quantity_updated = True
        old_opening_quantity = getattr(instance, 'old_opening_g_quantity', None)

        if old_opening_quantity is not None:
            opening_quantity_diffrence = instance.opening_quantity - old_opening_quantity
        


    
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


    
    if opening_quantity_updated:
        old_opening_godown_id = getattr(instance, 'old_opening_godown_id', None) 
        

        if old_opening_godown_id:
            
            
            if old_opening_godown_id == new_opening_godown:

                
                get_obj = item_godown_quantity_through_table.objects.get(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + opening_quantity_diffrence 
                get_obj.save()



            
            elif old_opening_godown_id != new_opening_godown and instance.opening_quantity == old_opening_quantity:
                
                
                
                decrease_obj_q = item_godown_quantity_through_table.objects.get(godown_name=old_opening_godown_id,Item_shade_name=item_shade_instance)
                decrease_obj_q.item_rate = opening_rate
                decrease_obj_q.quantity = decrease_obj_q.quantity - instance.opening_quantity 
                decrease_obj_q.save()

                
                
                get_obj , created = item_godown_quantity_through_table.objects.get_or_create(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + instance.opening_quantity 
                get_obj.save()
        


            
            elif old_opening_godown_id != new_opening_godown and instance.opening_quantity != old_opening_quantity:
                
                
                
                decrease_obj_q = item_godown_quantity_through_table.objects.get(godown_name=old_opening_godown_id, Item_shade_name=item_shade_instance)
                decrease_obj_q.item_rate = opening_rate
                decrease_obj_q.quantity = decrease_obj_q.quantity - old_opening_quantity
                decrease_obj_q.save()

                
                get_obj , created = item_godown_quantity_through_table.objects.get_or_create(godown_name=new_opening_godown,Item_shade_name=item_shade_instance)
                get_obj.item_rate = opening_rate
                get_obj.quantity = get_obj.quantity + instance.opening_quantity
                get_obj.save()





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
        
        logger.error(f"No item_godown_quantity_through_table entry found for item_id {item_id} and godown_id {godown_id}")
        print(f"No item_godown_quantity_through_table entry found for item_id {item_id} and godown_id {godown_id}")

    except Exception as e:
        
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        



@receiver(post_save, sender=RawStockTrasferRecords)
def created_updated_raw_stock_trasfer(sender, instance, created, **kwargs):

    source_godown_value = instance.master_instance.source_godown
    destination_godown_value = instance.master_instance.destination_godown

    if created:
        item_shade = instance.item_shade_transfer
        item_quantity = instance.item_quantity_transfer

        item_to_godown_quantity_through_source = item_godown_quantity_through_table.objects.get(
            godown_name=source_godown_value,Item_shade_name=item_shade)
        
        item_to_godown_quantity_through_source.quantity = item_to_godown_quantity_through_source.quantity - item_quantity
        item_to_godown_quantity_through_source.save()


        item_to_godown_quantity_through_destination, created = item_godown_quantity_through_table.objects.get_or_create(
            godown_name=destination_godown_value,Item_shade_name=item_shade)

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





@receiver(post_save, sender=purchase_voucher_items)
def set_item_rate_on_purchase(sender, instance, created, **kwargs):
    item_rate = instance.rate
    item_shade_id = instance.item_shade.id

    if item_shade_id:
        item_instance = item_color_shade.objects.get(id=item_shade_id)
        item_instance.rate = item_rate
        item_instance.save()



@receiver(post_save, sender = opening_shade_godown_quantity)
def set_item_rate_on_purchase(sender, instance, created, **kwargs):
    item_rate = instance.opening_rate
    item_shade_id = instance.opening_purchase_voucher_godown_item.id

    if item_shade_id:
        item_instance = item_color_shade.objects.get(id=item_shade_id)
        item_instance.rate = item_rate
        item_instance.save()



@receiver(post_save, sender=purchase_order)
def set_purchase_order_product_status(sender, instance, created, **kwargs):
    if created:
        purchase_order_id = instance
        purchase_order_id.process_status = '1'
        purchase_order_id.save()


 


@receiver(pre_save, sender=purchase_order_to_product)
def handle_purchase_order_update(sender, instance, **kwargs):
    if instance.id:
        previous_instance = purchase_order_to_product.objects.get(id=instance.id)
        previous_purchase_order_qty = previous_instance.order_quantity
        
        if  previous_purchase_order_qty != instance.order_quantity:
            purchase_order_raw_instances = purchase_order_for_raw_material.objects.filter(purchase_order_id=previous_instance.purchase_order_id)

            for instances in purchase_order_raw_instances:
                instances.delete()



    

@receiver(post_save, sender = purchase_order_for_raw_material_cutting_items)
def raw_material_cutting_items_cancelled(sender, instance, created, **kwargs):
    
    if instance.entry_from_cutting_room == True:
        
        if instance.material_color_shade.items.Fabric_nonfabric == 'Fabric' and instance.total_comsumption != 0:

            instance_material_color_shade = instance.material_color_shade.id
            instance_particular = instance.purchase_order_cutting.purchase_order_id.ledger_party_name.name
            instance_voucher_type = instance.purchase_order_cutting.factory_employee_id.factory_emp_name
            instance_voucher_number = instance.purchase_order_cutting.raw_material_cutting_id
            instance_godown_id = instance.purchase_order_cutting.purchase_order_id.temp_godown_select.id
            instance_inward = False
            instance_total_comsumption = instance.total_comsumption
            instance_rate = instance.rate
            instance_p_o_id = instance.purchase_order_cutting.purchase_order_id.id
            instance_ref_no = instance.purchase_order_cutting.purchase_order_id.product_reference_number.Product_Refrence_ID
            instance_cutting_id = instance.purchase_order_cutting.raw_material_cutting_id

            if instance.cutting_room_status == 'cutting_room':

                godown_item_report_for_cutting_room.objects.create(particular = instance_particular,
                                                                voucher_type= f'Pur.V Cutting/{instance_voucher_type}',
                                                                voucher_number = instance_voucher_number,material_color_shade = instance_material_color_shade ,
                                                                godown_id= instance_godown_id,
                                                                inward = instance_inward ,total_comsumption = instance_total_comsumption,
                                                                rate = instance_rate,p_o_id=instance_p_o_id,product_ref_no=instance_ref_no,cutting_pk=instance_cutting_id)

            elif instance.cutting_room_status == 'cutting_room_cancelled':

                
                instance_inward = True

                godown_item_report_for_cutting_room.objects.create(particular = instance_particular,
                                                                voucher_type=f'Pur.V Cutting-cancelled/{instance_voucher_type}'
                                                                ,voucher_number = instance_voucher_number,material_color_shade = instance_material_color_shade ,
                                                                godown_id= instance_godown_id,
                                                                inward = instance_inward ,total_comsumption = instance_total_comsumption,
                                                                rate = instance_rate,p_o_id=instance_p_o_id,product_ref_no=instance_ref_no,cutting_pk=instance_cutting_id)



@receiver(pre_delete, sender=product_purchase_voucher_items)
def handle_product_invoice_items_godowns_delete(sender, instance, **kwargs):
    product_instance = instance.product_name
    warehouse_instance = instance.product_purchase_master.finished_godowns
    qty = instance.quantity_total

    if product_instance and warehouse_instance: 

        try:
            product_2_warehouse_instance = Product_warehouse_quantity_through_table.objects.get(warehouse=warehouse_instance,product=product_instance)
        
        except ObjectDoesNotExist:
            product_2_warehouse_instance = Product_warehouse_quantity_through_table.objects.create(warehouse=warehouse_instance, product=product_instance)

        product_2_warehouse_instance.quantity = product_2_warehouse_instance.quantity - qty
        product_2_warehouse_instance.save()



@receiver(post_save, sender=Product_warehouse_quantity_through_table)
def delete_product_warehouse_quantity_if_0(sender, instance, created, **kwargs):
    
    if not created:  
        quantity_after_save = instance.quantity
        if quantity_after_save == 0:
            logger.info(f"product warehouse quantity instance deleted as quantity is 0, id - {instance.id}, - {instance.warehouse.warehouse_name_finished}, - {instance.product.PProduct_SKU}")
            instance.delete()




@receiver(post_save, sender=Finished_goods_transfer_records)
def create_update_warehouse_stock_transfer(sender, instance, created, **kwargs):
    product = instance.product
    quantity = instance.product_quantity_transfer
    master_instance = instance.Finished_goods_Stock_TransferMasterinstance

    godown = master_instance.source_warehouse
    warehouse = master_instance.destination_warehouse

    if created:
        
        godown_qty_value, created = product_godown_quantity_through_table.objects.get_or_create(godown_name = godown,product_color_name=product)
        godown_qty_value.quantity = godown_qty_value.quantity - quantity
        godown_qty_value.save()

    else:
        pass





"""
        or in forms
            def clean(self):
        cleaned_data = super().clean()
        
        value1 = cleaned_data.get('field1')
        value2 = cleaned_data.get('field2')
        value3 = cleaned_data.get('field3')

        
        if value1 and value2 and value3:
            autofill_value = f'{value1}-{value2}-{value3}'
            cleaned_data['autofill_field'] = autofill_value

        return cleaned_data
"""