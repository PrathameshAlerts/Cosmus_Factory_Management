from django.contrib import admin

# Register your models here.

from . models import Item_Creation, Product , Product2Category , MainCategory , Color , ProductImage,PProduct_Creation


admin.site.register(Product)
admin.site.register(Product2Category)
admin.site.register(Color)
admin.site.register(ProductImage)
admin.site.register(MainCategory)
admin.site.register(PProduct_Creation)
admin.site.register(Item_Creation)