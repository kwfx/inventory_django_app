from django.urls import path
from .views import (SearchInventoryView, InventoryFormView, InventoryListView, 
    InventoryCreate, InventoryUpdate, delete_line, delete_inventory)

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list_view"),
    path("<uuid:pk>/", InventoryFormView.as_view(), name="inventory_form_view"),
    path("search", SearchInventoryView.as_view(), name="search_inventory"),
    path("create/", InventoryCreate.as_view(), name="inventory_create"),
    path('update/<uuid:pk>/', InventoryUpdate.as_view(), name='inventory_update'),
    path('delete-line/<int:pk>', delete_line, name='delete_line'),
    path('delete-inventory/<uuid:pk>', delete_inventory, name='delete_inventory')
]
