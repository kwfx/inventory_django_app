from django.urls import path
from .views import (InventoryListView, ProductListView, ProductUpdateView, ProductCreateView,
    InventoryCreateView, InventoryUpdateView, search_product_by_oldref, delete_record, StockListView, stock_import_controller)

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list_view"),
    path("products", ProductListView.as_view(), name="product_list_view"),
    path("stock", StockListView.as_view(), name="stock_list_view"),
    path("create/", InventoryCreateView.as_view(), name="inventory_create"),
    path('update/<uuid:pk>/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/update/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<model_name>/<uuid:pk>', delete_record, name='product_delete'),
    path('search_product_by_oldref/<old_ref>/', search_product_by_oldref, name='search_product_by_oldref'),
    path('stock/import', stock_import_controller, name='stock_import_controller'),
]
