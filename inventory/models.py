from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
import math
from datetime import datetime

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    internal_ref = models.CharField(max_length=200, verbose_name="Référence interne")
    old_ref = models.CharField(max_length=200, verbose_name="Ancien référence")
    designation = models.CharField(max_length=200, verbose_name="Désignation")
    supplier = models.CharField(max_length=200, verbose_name="Fournisseur")
    sale_uom = models.CharField(max_length=20, choices=[
        ("unit", "Unité"),
        ("coffret", "Coffret"),
        ("FL", "FL"),
        ("BTE", "Boite"),
        ("carton", "Carton"),
        ("mc", "MC"),
    ], default="unit", verbose_name="Unité de vente")

    def __str__(self):
        return f"{self.internal_ref} - {self.designation}"

    def get_absolute_url(self):
        return reverse("product_form_view", args=[self.id])


class Zone(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"Zone : {self.name}"
    

class Inventory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="inventories")
    name_agent = models.CharField("Nom de l’agent d’inventaire", max_length=200)
    num_inventory = models.IntegerField("Nombre de comptage")

    def get_absolute_url(self):
        return reverse("inventory_update", args=[self.id])
    
    def __str__(self) -> str:
        return f"Inventaire : {self.zone} - Comptage: {self.num_inventory}"
    

class InventoryProductLines(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="inventory_product_lines")

    @property
    def product_supplier(self):
        return self.product.supplier


class ProductLotLines(models.Model):
    lot = models.CharField(max_length=200)
    quantity = models.FloatField("Quantité")
    quantity_uom = models.CharField(max_length=20, choices=[
        ("unit", "Unité"),
        ("coffret", "Coffret"),
        ("FL", "FL"),
        ("BTE", "Boite"),
        ("carton", "Carton"),
        ("mc", "MC"),
    ], default="unit")
    expiration_date = models.DateField("Date péremption", null=True, blank=True)
    inventory_product_line = models.ForeignKey(InventoryProductLines, on_delete=models.CASCADE, related_name="product_lot_lines")
