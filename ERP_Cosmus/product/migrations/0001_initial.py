# Generated by Django 4.2.5 on 2024-03-12 11:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_group', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccountSubGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_sub_group', models.CharField(max_length=50, unique=True)),
                ('acc_grp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.accountgroup')),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fabric_Group_Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fab_grp_name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Godown_finished_goods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('godown_name_finished', models.CharField(max_length=225)),
            ],
        ),
        migrations.CreateModel(
            name='Godown_raw_material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('godown_name_raw', models.CharField(max_length=225)),
            ],
        ),
        migrations.CreateModel(
            name='gst',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gst_percentage', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=250)),
                ('parent', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PProduct_Creation',
            fields=[
                ('PProduct_image', models.ImageField(blank=True, null=True, upload_to='pproduct/images')),
                ('PProduct_SKU', models.BigIntegerField(primary_key=True, serialize=False)),
                ('Product_EANCode', models.CharField(blank=True, max_length=100, null=True)),
                ('product_Video_URL', models.URLField(blank=True, null=True)),
                ('Product_Rating', models.FloatField(blank=True, null=True)),
                ('Amazon_Link', models.URLField(blank=True, null=True)),
                ('Flipkart_Link', models.URLField(blank=True, null=True)),
                ('Cosmus_link', models.URLField(blank=True, null=True)),
                ('PProduct_color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='production_primary_color', to='product.color')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Product_Name', models.CharField(blank=True, max_length=255)),
                ('Model_Name', models.CharField(blank=True, max_length=255)),
                ('Product_Brand', models.CharField(blank=True, choices=[('Cosmus', 'Cosmus'), ('Killer', 'Killer'), ('Tuffgear', 'Tuffgear'), ('BeeArmour', 'BeeArmour'), ('INIT', 'INIT'), ('OEM', 'OEM')], default='Cosmus', max_length=200)),
                ('Product_Status', models.CharField(blank=True, choices=[('Preproduction', 'Preproduction'), ('Active', 'Active'), ('Inactive', 'Inactive'), ('Discontinued', 'Discontinued')], default='Active', max_length=100)),
                ('Product_Channel', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Ecommerce', 'Ecommerce'), ('Retail', 'Retail'), ('Corporate', 'Corporate'), ('Modern Trade', ' Modern Trade'), ('Export', ' Export')], max_length=100, null=True)),
                ('Product_Refrence_ID', models.PositiveIntegerField(unique=True)),
                ('Product_Cost_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('Product_MRP', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('Product_SalePrice_CustomerPrice', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('Product_BulkPrice', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('Product_WarrantyTime', models.CharField(blank=True, choices=[('0 Months', '0 Months'), ('6 Months', '6 Months'), ('12 Months', '12 Months'), ('18 Months', '18 Months'), ('24 Months', '24 Months'), ('30 Months', '30 Months'), ('36 Months', '36 Months'), ('42 Months', '42 Months'), ('48 Months', '48 Months'), ('54 Months', '54 Months'), ('60 Months', '60 Months')], default='0 Months', max_length=15)),
                ('Product_HSNCode', models.BigIntegerField(blank=True, default='12345678')),
                ('Product_ShortName', models.CharField(blank=True, max_length=200, null=True)),
                ('Product_Compartments', models.CharField(blank=True, choices=[('One', 'One'), ('Two', 'Two'), ('Three', 'Three'), ('Four', 'Four'), ('Five', 'Five'), ('Six', 'Six'), ('Seven', 'Seven'), ('Eight', 'Eight'), ('Nine', 'Nine'), ('Ten', 'Ten')], max_length=50, null=True)),
                ('Product_UOM', models.CharField(blank=True, choices=[('Pcs', 'Pcs'), ('Set of 3', 'Set of 3')], max_length=50, null=True)),
                ('Product_Accessory_Compartments', models.CharField(blank=True, choices=[('One', 'One'), ('Two', 'Two'), ('Three', 'Three'), ('Four', 'Four'), ('Five', 'Five'), ('Six', 'Six'), ('Seven', 'Seven'), ('Eight', 'Eight'), ('Nine', 'Nine'), ('Ten', 'Ten')], max_length=20, null=True)),
                ('Product_CapacityLtrs', models.PositiveIntegerField(blank=True, null=True)),
                ('Product_Material', models.CharField(blank=True, choices=[('PU Coated Polyester', 'PU Coated Polyester'), ('PU Coated Nylon', 'PU Coated Nylon'), ('Vegan Leather', 'Vegan Leather'), ('Polycarbonate', 'Polycarbonate'), ('Eva Shell', 'Eva Shell'), ('Cotton', 'Cotton'), ('Jute', 'Jute')], max_length=100, null=True)),
                ('Product_BulletPoint1', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_BulletPoint2', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_BulletPoint3', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_BulletPoint4', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_BulletPoint5', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_ShortDescription', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_LongDescription', models.CharField(blank=True, max_length=255, null=True)),
                ('Product_Dimensions_WP_Length', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WP_Width', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WP_Height', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WP_Weight', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WOP_Length', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WOP_Width', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WOP_Height', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_Dimensions_WOP_Weight', models.CharField(blank=True, max_length=150, null=True)),
                ('Product_WRP', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('Product_CashCounterPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('Product_IndiaMartPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('Product_Retailer_dealer_Price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('Product_Wholesaler_DistributorPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('Product_Create_Date', models.DateField(auto_now=True)),
                ('Product_Gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Unisex', 'Unisex')], max_length=15, null=True)),
                ('Product_QtyPerBox', models.IntegerField(blank=True, null=True)),
                ('Product_GST', models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.PROTECT, to='product.gst')),
            ],
        ),
        migrations.CreateModel(
            name='RawStockTransfer',
            fields=[
                ('voucher_no', models.AutoField(primary_key=True, serialize=False)),
                ('source_godown', models.CharField(max_length=200)),
                ('destination_godown', models.CharField(max_length=200)),
                ('item_name_transfer', models.CharField(max_length=200)),
                ('item_color_transfer', models.CharField(max_length=200)),
                ('item_shade_transfer', models.CharField(max_length=200)),
                ('item_quantity_transfer', models.CharField(max_length=200)),
                ('item_unit_transfer', models.CharField(max_length=200)),
                ('remarks', models.CharField(max_length=255)),
                ('date_and_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit_Name_Create',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_item_name', models.CharField(max_length=150, unique=True)),
                ('acc_sub_grp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.accountsubgroup')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Image', models.ImageField(blank=True, null=True, upload_to='product/images')),
                ('Image_type', models.CharField(blank=True, choices=[('Main Image', 'Main Image'), ('White Background', 'White Background'), ('Model Image', 'Model Image'), ('Catalogue Image', 'Catalogue Image')], max_length=100, null=True)),
                ('Order_by', models.IntegerField(blank=True, null=True)),
                ('Image_Uploaded_at', models.DateTimeField(auto_now=True)),
                ('Image_Modified_at', models.DateTimeField(auto_now_add=True)),
                ('Product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productimages', to='product.pproduct_creation')),
            ],
        ),
        migrations.CreateModel(
            name='Product2Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.maincategory')),
                ('Product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
        migrations.AddField(
            model_name='pproduct_creation',
            name='Product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productdetails', to='product.product'),
        ),
        migrations.CreateModel(
            name='Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('short_name', models.CharField(blank=True, max_length=100)),
                ('vendor_code', models.CharField(blank=True, max_length=100)),
                ('maintain_billwise', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=30)),
                ('default_credit_period', models.CharField(blank=True, max_length=100)),
                ('types', models.CharField(blank=True, choices=[('Trader', 'Trader'), ('Manufacture', 'Manufacture')], max_length=30)),
                ('Gst_no', models.CharField(blank=True, max_length=100)),
                ('date', models.DateField(auto_now=True)),
                ('address', models.TextField(blank=True)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('country', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('pincode', models.IntegerField()),
                ('mobile_no', models.BigIntegerField()),
                ('landline_no', models.BigIntegerField()),
                ('bank_details', models.TextField(blank=True)),
                ('Debit_Credit', models.CharField(blank=True, choices=[('Debit', 'Debit'), ('Credit', 'Credit')], max_length=255)),
                ('under_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.accountsubgroup')),
            ],
        ),
        migrations.CreateModel(
            name='Item_Creation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255, unique=True)),
                ('Material_code', models.CharField(max_length=255)),
                ('Packing', models.CharField(choices=[('Roll', 'Roll'), ('Bundle', 'Bundle')], max_length=255)),
                ('Units', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Panha', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Fabric_nonfabric', models.CharField(choices=[('Fabric', 'Fabric'), ('Non Fabric', 'Non Fabric')], max_length=255)),
                ('Fabric_Finishes', models.CharField(choices=[('PVC Coating', 'PVC Coating'), ('PU Coating', 'PU Coating'), ('Black Nickle', 'Black Nickle'), ('polypropylene(PP)', 'polypropylene(PP)')], max_length=255)),
                ('HSN_Code', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('Unused', 'Unused'), ('Used', 'Used'), ('Slow Moving', 'Slow Moving'), ('Dead', 'Dead')], max_length=50)),
                ('item_shade_image', models.ImageField(blank=True, null=True, upload_to='rawmaterial/images')),
                ('Fabric_Group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.fabric_group_model')),
                ('Item_Color', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ItemColor', to='product.color')),
                ('Item_Creation_GST', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.gst')),
                ('unit_name_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.unit_name_create')),
            ],
        ),
        migrations.CreateModel(
            name='item_color_shade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name_rank', models.PositiveIntegerField(blank=True, null=True)),
                ('item_shade_name', models.CharField(blank=True, max_length=100, null=True)),
                ('item_color_image', models.ImageField(blank=True, null=True, upload_to='rawmaterial/images')),
                ('items', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shades', to='product.item_creation')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=255)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='account_credit_debit_master_table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('account_name', models.CharField(max_length=100)),
                ('voucher_no', models.IntegerField(blank=True, null=True)),
                ('voucher_type', models.CharField(max_length=100)),
                ('particulars', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now=True)),
                ('modified_date_time', models.DateTimeField(auto_now_add=True)),
                ('ledger', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transaction_entry', to='product.ledger')),
            ],
        ),
        migrations.CreateModel(
            name='item_godown_quantity_through_table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('Item_shade_name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='godown_shades', to='product.item_color_shade')),
                ('godown_name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='raw_godown_names', to='product.godown_raw_material')),
            ],
            options={
                'unique_together': {('godown_name', 'Item_shade_name')},
            },
        ),
    ]
