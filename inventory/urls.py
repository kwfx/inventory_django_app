from django.urls import path
from .views import (InventoryListView, 
    InventoryCreateView, InventoryUpdateView, delete_inventory, get_product_data, ProductAutocomplete)

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list_view"),
    # path("<uuid:pk>/", InventoryFormView.as_view(), name="inventory_form_view"),
    path("create/", InventoryCreateView.as_view(), name="inventory_create"),
    path('update/<uuid:pk>/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('delete-inventory/<uuid:pk>', delete_inventory, name='delete_inventory'),
    path('get-product-data/<uuid:pk>', get_product_data, name='get_product_data'),
    path('product-autocomplete',
        ProductAutocomplete,
        name='product_autocomplete',
    ),
]
