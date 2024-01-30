from django.contrib import admin

# Register your models here.

from . models import Product , Product2Category , MainCategory , Color , ProductImage,PProduct_Creation, item_name


admin.site.register(Product)
admin.site.register(Product2Category)
admin.site.register(Color)
admin.site.register(ProductImage)
admin.site.register(MainCategory)
admin.site.register(PProduct_Creation)
admin.site.register(item_name)