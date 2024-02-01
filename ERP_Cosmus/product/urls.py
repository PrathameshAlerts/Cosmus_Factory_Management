from django.urls import path
from . import views



urlpatterns = [
    #authentication routes
    path('login/',views.login , name= 'login'),
    path('register/',views.register , name= 'register'),

    #erp routes
    path('index/', views.index, name= 'index'),
    path('listproduct/', views.listproduct, name= 'listproduct'),
    path('editproduct/<int:pk>',views.edit_product , name= 'edit_product'),
    path('addproduct/',views.add_product , name= 'add_product'),
    path('aplus/',views.aplus , name= 'aplus'),
    path('deleteproduct/<int:pk>',views.deleteproduct , name= 'deleteproduct'),
    path(' ',views.index , name= 'index'),

    #factoryroutes
    #product_routes
    path('editpproduct/<int:pk>',views.edit_production_product , name= 'edit_production_product'),
    path('pproduct_creation/',views.product_color_sku , name= 'pproduct_creation'),
    path('pproductlist/',views.pproduct_list ,name= 'pproductlist'),
    path('pproductdelete/<int:pk>',views.pproduct_delete, name= 'pproductdelete'),

    #color routes
    path('colorlist/',views.color_list, name= 'colorlist'),
    path('colordelete/<slug:slug>',views.color_delete,name= 'colordelete'),
    path('colorcreate/',views.color_create, name='colorcreate'),
    path('coloredit/<slug:slug>',views.color_edit, name= 'coloredit'),

    #item_routes
    path('itemedit/<int:pk>',views.item_edit , name= 'item-edit'),
    path('itemcreate/',views.item_create , name= 'item-create'),
    path('itemlist/',views.item_list ,name= 'item-list'),
    path('itemdelete/<int:pk>',views.item_delete , name= 'item-delete'),

    #itemfabgroup
    path('itemfabricgroupcreate/',views.item_fabric_group_create , name= 'item-fabgroup-create'),
    path('itemfabricgroupupdate/<slug:slug>',views.item_fabric_group_update , name= 'item-fabgroup-update'),
    path('itemfabricgrouplist/',views.item_fabric_group_list , name= 'item-fabgroup-list'),
    path('itemfabricgroupdelete/<slug:slug>',views.item_fabric_group_delete , name= 'item-fabgroup-delete'),

    #itemname
    path('itemnamecreate/',views.item_name_create , name= 'item-name-create'),
    path('itemnameupdate/<slug:slug>',views.item_name_update , name= 'item-name-update'),
    path('itemnamelist/',views.item_name_list , name= 'item-name-list'),
    path('itemnamedelete/<slug:slug>',views.item_name_delete , name= 'item-name-delete'),


    #unitname
    path('unitnamecreate/',views.unit_name_create , name= 'unit_name-create'),
    path('unitnameupdate/<slug:slug>',views.unit_name_update , name= 'unit_name-update'),
    path('unitnamelist/',views.unit_name_list , name= 'unit_name-list'),
    path('unitnamedelete/<slug:slug>',views.unit_name_delete , name= 'unit_name-delete'),

    #common Routes
    path('allmaster/', views.allmaster , name= 'all-master')

]