from django.contrib import admin

# Register your models here.

from . models import AccountGroup, AccountSubGroup,   Product ,  gst,MainCategory ,Color , ProductImage,PProduct_Creation, StockItem, item_godown_quantity_through_table 

class PProductCreationInline(admin.TabularInline):
    model = PProduct_Creation
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [PProductCreationInline]

admin.site.register(Product, ProductAdmin)

admin.site.register(Color)
admin.site.register(ProductImage)
admin.site.register(MainCategory)
admin.site.register(PProduct_Creation)
admin.site.register(AccountGroup)
admin.site.register(AccountSubGroup)
admin.site.register(StockItem)
admin.site.register(gst)
admin.site.register(item_godown_quantity_through_table)










