import json
import os
from typing import Any
import openpyxl
from io import BytesIO

from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, CreateView, UpdateView, FormView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Inventory, Product, InventoryProductLines, ProductLotLines, Zone, SystemStock
from .forms import ProductLotLinesFormSet, InventoryFormSet, SearchForm, StockImportForm
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.db.models import Q
from django import forms
from django.contrib import messages
from django.core import serializers
from django.views.generic.detail import SingleObjectMixin
from django.apps import apps



class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "product_list"
    template_name = "inventory/prod_list.html"
    ordering = ['old_ref']
    login_url = "account_login"


class StockListView(LoginRequiredMixin, ListView):
    model = SystemStock
    context_object_name = "stock_list"
    template_name = "inventory/system_stock_list.html"
    ordering = ['product__internal_ref']
    login_url = "account_login"


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    context_object_name = "inventory_list"
    template_name = "inventory/inventory_list.html"
    ordering = ['zone', 'num_inventory']
    login_url = "account_login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone_id = self.request.GET.get("zone")
        num_inv = self.request.GET.get("num_inv")
        product_ref = self.request.GET.get("product_ref")
        searched_product_ids = None
        if product_ref:
            searched_product_ids = list(Product.objects.all().filter(Q(internal_ref__icontains=product_ref) |
                                                           Q(old_ref__icontains=product_ref)).values_list("id", flat=True))
        search_form = SearchForm(initial={'zone': zone_id, 'num_inv': num_inv, 'product_ref': product_ref})
        choices = [('', '')]
        if zone_id:
            choices.extend([(inv.num_inventory, inv.num_inventory) for inv in Inventory.objects.all().filter(Q(zone__id=zone_id))])
        search_form.fields["num_inv"].choices = choices
        context['search_form'] = search_form
        context['searched_product_ids'] = searched_product_ids
        return context

    def get_queryset(self) -> QuerySet[Any]:
        zone_id = self.request.GET.get("zone")
        num_inventory = self.request.GET.get("num_inv")
        filter = Q()
        if zone_id:
            filter = Q(zone__id=zone_id)
            if num_inventory:
                filter &= Q(num_inventory=num_inventory)
        return self.model.objects.all().filter(filter).order_by(*self.ordering)


class ProductUpdateView(UpdateView):
    model = Product
    template_name = "inventory/product_form_view.html"
    fields = "__all__"

class ProductCreateView(CreateView):
    model = Product
    template_name = "inventory/product_form_view.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse('product_list_view')

class InventoryCreateView(CreateView):
    model = Inventory
    template_name = "inventory/inv_create.html"
    fields = [
        "zone", "num_inventory", "name_agent"
    ]

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             "The Inventory was added.")
        return super().form_valid(form)


class InventoryUpdateView(SingleObjectMixin, FormView):
    """
    For adding books to a Inventory, or editing them.
    """

    model = Inventory
    template_name = "inventory/inv_update.html"
    fields = [
        "zone", "num_inventory", "name_agent"
    ]

    def get(self, request, *args, **kwargs):
        # The Inventory we're editing:
        self.object = self.get_object(queryset=Inventory.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # The Inventory we're uploading for:
        self.object = self.get_object(queryset=Inventory.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """
        Use our big formset of formsets, and pass in the Publisher object.
        """
        return InventoryFormSet(
            **self.get_form_kwargs(), instance=self.object
        )

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, "Changes were saved.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("inventory_list_view")

def delete_record(request, model_name, pk):
    if request.user.is_authenticated:
        Model = apps.get_model("inventory." + model_name)
        record = Model.objects.get(id=pk)
        record.delete()
        return HttpResponse(f'{model_name.capitalize()} {pk} has been deleted successfully.', status=200)
    return HttpResponse(f'Not allowed', status=401)

def search_product_by_oldref(request, old_ref):
    try:
        res_search = Product.objects.all().filter(old_ref__istartswith=old_ref).first()
        if res_search:
            res_search.sale_uom = res_search.get_sale_uom_display()
            product_data = [res_search] 
        else:
            product_data = []
        json_data = serializers.serialize('json', product_data)
        return HttpResponse(json_data, content_type='application/json')
    except Exception as er:
        print(er)
        return HttpResponse(er, content_type='application/json')
    

def stock_import_controller(request):
    if request.method == "POST":
        try:
            xls_file = request.FILES['xls_file']
            file_extension = os.path.splitext(xls_file.name)[1]
            if not xls_file or file_extension not in (".xls", ".xlsx"):
                raise Exception("Vous devez charger des fichiers excel (xls ou xlsx)")
            book = openpyxl.load_workbook(filename=BytesIO(xls_file.read()))
            sh = book.worksheets[0]
            if sh.max_row:
                SystemStock.objects.all().delete()
            for row in sh.iter_rows(min_row=2):
                (internal_ref, old_ref, designation, lot, exp_date,
                    qty, qty_uom, supplier, sale_uom) = [c.value for c in row]
                product = Product.objects.all().filter(internal_ref=internal_ref, old_ref=old_ref).first()
                if not product:
                    product = Product(internal_ref=internal_ref, old_ref=old_ref, 
                            designation=designation, supplier=supplier, sale_uom=sale_uom)
                    product.save()
                stock = SystemStock(product=product, lot=lot, expiration_date=exp_date, quantity_uom = qty_uom, quantity=qty)
                stock.save()
            return HttpResponseRedirect(reverse("stock_list_view"))
        except Exception as ex:
            return HttpResponseServerError(str(ex))
    return render(request, "inventory/stock_import.html", {"form": StockImportForm})    


def StockComparisonView(request, inventory_id):
    inventory = Inventory.objects.get(id=inventory_id)
    lines = []
    for product_line in inventory.inventory_product_lines.all():
        for lotline in product_line.product_lot_lines.all():
            stock_line = SystemStock.objects.filter(product=product_line.product, lot=lotline.lot).first()
            quantity_system = stock_line.quantity if stock_line else 0
            lines.append({
                "internal_ref": product_line.product.internal_ref,
                "old_ref": product_line.product.old_ref,
                "designation": product_line.product.designation,
                "lot": lotline.lot,
                "expiration_date": str(lotline.expiration_date),
                "supplier": product_line.product.supplier,
                "quantity_uom": lotline.quantity_uom,
                "quantity": lotline.quantity,
                "quantity_system": quantity_system,
                "ecart": lotline.quantity - quantity_system,
            })
    return render(request, "inventory/stock_comparison.html", {"lines": lines}) 