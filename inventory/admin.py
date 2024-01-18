from django.contrib import admin

from .models import Product, Inventory, InventoryLines, Zone


class InventoryLinesInline(admin.TabularInline):
    model = InventoryLines


class InventoryAdmin(admin.ModelAdmin):
    inlines = [
        InventoryLinesInline,
    ]
    list_display = ("zone", "name_agent", "num_inventory", "product")
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ("internal_ref", "old_ref", "designation")
    

class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", )


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Zone, ZoneAdmin)