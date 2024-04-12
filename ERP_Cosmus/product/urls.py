from django.urls import path
from . import views



urlpatterns = [
    #authentication routes
    path('login/',views.login , name='login'),
    path('register/',views.register , name= 'register'),

    #factoryroutes
    #product_routes
    path('editpproduct/<int:pk>',views.edit_production_product , name= 'edit_production_product'),
    path('pproduct_creation/',views.product_color_sku , name='pproduct_creation'),
    path('pproduct_creation_ref_id/<int:ref_id>',views.product_color_sku , name= 'pproduct-creation-with-ref-id'),
    path('pproductlist/',views.pproduct_list ,name= 'pproductlist'),
    path('pproductdelete/<int:pk>',views.pproduct_delete, name= 'pproductdelete'),

    #productandcategory
    path('definemaincategoryproduct/',views.definemaincategoryproduct, name= 'define-main-category-product'),
    path('definemaincategoryupdateproduct/<int:pk>',views.definemaincategoryproduct, name= 'define-main-category-update-product'),
    path('definemaincategoryproductdelete/<int:pk>',views.definemaincategoryproductdelete, name= 'define-main-category-delete-product'),

    path('definesubcategoryproduct/',views.definesubcategoryproduct, name= 'define-sub-category-product'),
    path('definesubcategoryupdateproduct/<int:pk>',views.definesubcategoryproduct, name= 'define-sub-category-update-product'),
    path('definesubcategoryproductdelete/<int:pk>',views.definesubcategoryproductdelete, name= 'define-sub-category-product-delete'),

    path('product2subcategoryupdate/<int:pk>',views.product2subcategory, name= 'product-2-subcategory-update'),
    path('product2subcategory/',views.product2subcategory, name= 'product-2-subcategory'),
    path('product2subcategoryajax/',views.product2subcategoryajax, name = 'product2subcategory-ajax'),
    path('product2subcategoryproductajax/', views.product2subcategoryproductajax, name = 'product2subcategoryajax'),

    #productImages
    path('product/<int:pk>/add_images/', views.add_product_images, name='add-product-images'),

    #productVideourl
    path('product/<int:pk>/add_video_url/', views.add_product_video_url, name='add-product-video-url'),


    #color routes
    #color modal routes
    # path('colorlist/',views.color_list, name= 'colorlist'),
    path('colordelete/<int:pk>',views.color_delete,name='colordelete'),
    path('colorcreate_update/',views.color_create_update, name='colorlist'),
    path('colorcreate_update/<int:pk>',views.color_create_update, name='coloredit'),

    # color in page
    path('simple_colorcreate_update/',views.color_create_update, name='simplecolorlist'),
    path('simple_colorcreate_update/<int:pk>',views.color_create_update, name='simplecolorlist'),
    path('simple_colorcreate_list/',views.color_create_update, name='simplecolorlistonly'),

    #color popup
    path('color_popup/',views.color_create_update, name='color-popup'),

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
    #popup
    path('fabric_popup/',views.item_fabric_group_create, name='fabric-popup'),


    #unitname
    path('unitnamecreate/',views.unit_name_create , name= 'unit_name-create'),
    path('unitnameupdate/<int:pk>',views.unit_name_update , name= 'unit_name-update'),
    path('unitnamelist/',views.unit_name_list , name= 'unit_name-list'),
    path('unitnamedelete/<int:pk>',views.unit_name_delete , name= 'unit_name-delete'),
    #popup
    path('units_popup/',views.unit_name_create, name='unit-name-popup'),

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

    #godown
    path('godowncreate/', views.godowncreate, name = 'godown-create'),
    path('godownupdateraw/<str:str>/<int:pk>', views.godownupdate, name = 'godown-update'),
    path('godownlist/', views.godownlist, name = 'godown-list'),
    path('godowndelete/<str:str>/<int:pk>', views.godowndelete, name = 'godown-delete'),


    #stocktransfer
    path('stocktransfer/', views.stocktransfer, name = 'stock-transfer'),


    #PurchaseVoucher
    path('purchasevouchercreate/', views.purchasevouchercreateupdate, name = 'purchase-voucher-create'),
    path('purchasevoucherupdate/<int:pk>', views.purchasevouchercreateupdate, name = 'purchase-voucher-update'),
    path('purchasevoucherlist/', views.purchasevoucherlist, name = 'purchase-voucher-list'),
    path('purchasevoucherdelete/<int:pk>', views.purchasevoucherdelete, name = 'purchase-voucher-delete'),
    path('purchasevoucherpopup/<int:shade_id>', views.purchasevoucherpopup, name='purchase-voucher-popup'),

    path('purchasevouchercreatepopupajax/',views.purchasevouchercreatepopupajax,name = 'purchasevoucher-createpopup-ajax'),

    #SalesVoucher
    path('salesvouchercreate/', views.salesvouchercreate, name = 'sales-voucher-create'),
    path('salesvoucherupdate/', views.salesvoucherupdate, name = 'sales-voucher-update'),
    path('salesvoucherlist/', views.salesvoucherlist, name = 'sales-voucher-list'),
    path('salesvoucherdelete/', views.salesvoucherdelete, name = 'sales-voucher-delete'),

    #subcategorys
    path('gstcreate/', views.gst_create_update, name = 'gst-create'),
    # path('gstupdate/<int:pk>', views.gst_create_update, name = 'gst-update'),
    path('gstlist/', views.gst_list, name = 'gst-list'),
    path('gstdelete/<int:pk>', views.gst_delete, name = 'gst-delete'),
    path('gstpopup/',views.gst_create_update, name = 'gst-popup'),


    path('fabricfinishesscreate/', views.fabric_finishes_create_update, name = 'fabric-finishes-create'),
    path('fabricfinishesupdate/<int:pk>', views.fabric_finishes_create_update, name = 'fabric-finishes-update'),
    path('fabricfinisheslist/', views.fabric_finishes_list, name = 'fabric-finishes-list'),
    path('fabricfinishesdelete/<int:pk>', views.fabric_finishes_delete, name = 'fabric-finishes-delete'),

    path('fabricfinishespopup/', views.fabric_finishes_create_update, name = 'fabric-finishes-popup'),


    path('packaging_create/', views.packaging_create_update, name = 'packaging-create'),
    path('packagingupdate/<int:pk>', views.packaging_create_update, name = 'packaging-update'),
    path('packaginglist/', views.packaging_list, name = 'packaging-list'),
    path('packagingdelete/<int:pk>', views.packaging_delete, name = 'packaging-delete'),
    
    path('packagingpop/',views.packaging_create_update, name = 'packaging-popup'),


    #reports
    path('stocktransferreport/', views.stocktransferreport, name = 'stock-transfer-report'),

    #common Routes
    path('', views.dashboard , name='dashboard-main'),


]