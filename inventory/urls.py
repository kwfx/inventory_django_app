from django.urls import path
from .views import (InventoryListView, 
    InventoryCreateView, InventoryUpdateView, delete_inventory, search_product_by_oldref, ProductAutocomplete)

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list_view"),
    # path("<uuid:pk>/", InventoryFormView.as_view(), name="inventory_form_view"),
    path("create/", InventoryCreateView.as_view(), name="inventory_create"),
    path('update/<uuid:pk>/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('delete-inventory/<uuid:pk>', delete_inventory, name='delete_inventory'),
    path('search_product_by_oldref/<old_ref>/', search_product_by_oldref, name='search_product_by_oldref'),
    path('product-autocomplete',
        ProductAutocomplete,
        name='product_autocomplete',
    ),
]
