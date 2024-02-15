from django.urls import path
from .views import (InventoryListView, ProductListView, ProductUpdateView, ProductCreateView,
    InventoryCreateView, InventoryUpdateView, product_details, delete_record, 
    StockComparisonView, StockListView, stock_import_controller, ProductAutocomplete, InventoryCompareView, export_data)

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list_view"),
    path("compare", InventoryCompareView.as_view(), name="inventory_compare_view"),
    path("products", ProductListView.as_view(), name="product_list_view"),
    path("stock", StockListView.as_view(), name="stock_list_view"),
    path("create/", InventoryCreateView.as_view(), name="inventory_create"),
    path('update/<uuid:pk>/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/update/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<model_name>/<uuid:pk>', delete_record, name='product_delete'),
    path('product_details/<uuid:pk>/', product_details, name='product_details'),
    path('stock/import', stock_import_controller, name='stock_import_controller'),
    path('stock_comparison/<inventory_id>/', StockComparisonView, name='stock_comparison'),
    path('product-autocomplete/', ProductAutocomplete, name='product_autocomplete'),
    path('export/<model_name>', export_data, name="export_data")
]
