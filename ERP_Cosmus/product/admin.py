from django.contrib import admin

# Register your models here.

from . models import AccountGroup, AccountSubGroup,  Product , Product2Category , gst,MainCategory ,Color , ProductImage,PProduct_Creation, StockItem 



admin.site.register(Product)
admin.site.register(Product2Category)
admin.site.register(Color)
admin.site.register(ProductImage)
admin.site.register(MainCategory)
admin.site.register(PProduct_Creation)
admin.site.register(AccountGroup)
admin.site.register(AccountSubGroup)
admin.site.register(StockItem)
admin.site.register(gst)





# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#     pass