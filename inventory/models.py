from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
import math

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    internal_ref = models.CharField(max_length=200)
    old_ref = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    supplier = models.CharField(max_length=200)
    sale_uom = models.CharField(max_length=20, choices=[
        ("unit", "Unité"),
        ("coffret", "Coffret"),
        ("FL", "FL"),
        ("BTE", "Boite"),
        ("carton", "Carton"),
        ("mc", "MC"),
    ], default="unit")

    def __str__(self):
        return f"Product : {self.internal_ref} - {self.designation}"

    def get_absolute_url(self):
        return reverse("product_form_view", args=[self.id])

    # def get_next_record(self):
    #     all_recs = Book.objects.all().order_by(self.orderby)
    #     if not all_recs: return
    #     next_records = all_recs.filter(id__gt=self.__dict__.get(self.orderby))
    #     if next_records:
    #         return reverse("book_form_view", args=[next_records.first().id])
    #     else:
    #         return reverse("book_form_view", args=[all_recs.first().id])

    # def get_previous_record(self):
    #     all_recs = Book.objects.all().order_by(f"-{self.orderby}")
    #     if not all_recs:
    #         return
    #     next_records = all_recs.filter(id__lt=self.__dict__.get(self.orderby))
    #     if next_records:
    #         return reverse("book_form_view", args=[next_records[0].id])
    #     return reverse("book_form_view", args=[all_recs.first().id])

    # @property
    # def overall_rate(self):
    #     return self.reviews.aggregate(overall_rate=models.Avg("rate"))["overall_rate"]

    # @property
    # def current_user_rate(self):
    #     if self.user.is_authenticated:
    #         user_rev = self.reviews.filter(user=self.user)
    #         return self.reviews.filter(user=self.user)[0].rate if user_rev else 0
    #     return 0


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")

    def get_absolute_url(self):
        return reverse("inventory_form_view", args=[self.id])
    
    def __str__(self) -> str:
        return f"Inventaire : {self.zone}"
    
class InventoryLines(models.Model):
    quantity = models.FloatField("Quantité")
    quantity_uom = models.CharField(max_length=20, choices=[
        ("unit", "Unité"),
        ("coffret", "Coffret"),
        ("FL", "FL"),
        ("BTE", "Boite"),
        ("carton", "Carton"),
        ("mc", "MC"),
    ], default="unit")
    expiration_date = models.DateField("Date péremption")
    lot = models.CharField(max_length=200)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="inventory_lines")
