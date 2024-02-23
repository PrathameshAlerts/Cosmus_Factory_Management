from django.urls import path
from . import views



urlpatterns = [
    #authentication routes
    path('login/',views.login , name='login'),
    path('register/',views.register , name= 'register'),

    #factoryroutes
    #product_routes
    path('editpproduct/<int:pk>',views.edit_production_product , name= 'edit_production_product'),
    path('pproduct_creation/',views.product_color_sku , name= 'pproduct_creation'),
    path('pproductlist/',views.pproduct_list ,name= 'pproductlist'),
    path('pproductdelete/<int:pk>',views.pproduct_delete, name= 'pproductdelete'),

    #color routes
    # path('colorlist/',views.color_list, name= 'colorlist'),
    path('colordelete/<int:pk>',views.color_delete,name='colordelete'),
    path('colorcreate_update/',views.color_create_update, name='colorlist'),
    path('colorcreate_update/<int:pk>',views.color_create_update, name='coloredit'),


    path('simple_colorcreate_update/',views.color_create_update, name='simplecolorlist'),
    path('simple_colorcreate_update/<int:pk>',views.color_create_update, name='simplecolorlist'),
    path('simple_colorcreate_list/',views.color_create_update, name='simplecolorlistonly'),

    #item_routes
    path('itemedit/<int:pk>',views.item_edit , name= 'item-edit'),
    path('itemcreate/',views.item_create , name= 'item-create'),
    path('itemlist/',views.item_list ,name= 'item-list'),
    path('itemdelete/<int:pk>',views.item_delete , name= 'item-delete'),

    #itemfabgroup
    path('itemfabricgroupcreate/',views.item_fabric_group_create , name= 'item-fabgroup-create'),
    path('itemfabricgroupupdate/<int:pk>',views.item_fabric_group_update , name= 'item-fabgroup-update'),
    path('itemfabricgrouplist/',views.item_fabric_group_list , name= 'item-fabgroup-list'),
    path('itemfabricgroupdelete/<int:pk>',views.item_fabric_group_delete , name= 'item-fabgroup-delete'),

    #unitname
    path('unitnamecreate/',views.unit_name_create , name= 'unit_name-create'),
    path('unitnameupdate/<int:pk>',views.unit_name_update , name= 'unit_name-update'),
    path('unitnamelist/',views.unit_name_list , name= 'unit_name-list'),
    path('unitnamedelete/<int:pk>',views.unit_name_delete , name= 'unit_name-delete'),

    #accountsubgrp
    path('accsubgrpcreate/',views.account_sub_group_create , name= 'account_sub_group-create'),
    path('accsubgrpupdate/<int:pk>',views.account_sub_group_update , name= 'account_sub_group-update'),
    path('accsubgrplist/',views.account_sub_group_list , name='account_sub_group-list'),
    path('accsubgrpdelete/<int:pk>',views.account_sub_group_delete , name= 'account_sub_group-delete'),

    #stockitem
    path('stockitemcreate/',views.stock_item_create , name= 'stock-item-create'),
    path('stockitemupdate/<int:pk>',views.stock_item_update , name= 'stock_item-update'),
    path('stockitemlist/',views.stock_item_list , name='stock_item-list'),
    path('stockitemdelete/<int:pk>',views.stock_item_delete , name= 'stock_item-delete'),


    #ledger
    path('ledgercreate/', views.ledgercreate, name = 'ledger-create'),
    path('ledgerupdate/<int:pk>', views.ledgerupdate, name = 'ledger-update'),
    path('ledgerlist/', views.ledgerlist, name = 'ledger-list'),
    path('ledgerdelete/<int:pk>', views.ledgerdelete, name = 'ledger-delete'),




    #common Routes
    path('', views.dashboard , name='dashboard-main'),


]