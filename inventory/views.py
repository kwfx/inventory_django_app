import json
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, CreateView, UpdateView, FormView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Inventory, Product, InventoryProductLines, ProductLotLines
from .forms import ProductLotLinesFormSet, InventoryFormSet
from django.http import HttpResponseRedirect
from django.db.models import Q
from django import forms
from django.contrib import messages
from django.core import serializers
from django.views.generic.detail import SingleObjectMixin
from dal import autocomplete


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    context_object_name = "inventory_list" # object_list in template => book_list
    template_name = "inventory/inventory_list.html"
    ordering = ['zone', 'num_inventory']
    login_url = "account_login"
    
    def get_queryset(self) -> QuerySet[Any]:
        searchby = self.request.GET.get("searchby")
        search_query = self.request.GET.get("q")
        if not search_query:
            return self.model.objects.all()
        else:
            if searchby == 'zone':
                q_filter = Q(zone__name__icontains=search_query)
            elif searchby == 'product':
                q_filter = Q(product__internal_ref__icontains=search_query)
            else:
                q_filter = Q(num_inventory=search_query)
            return self.model.objects.all().filter(q_filter)


class InventoryCreateView(CreateView):

    model = Inventory
    template_name = "inventory/inv_create.html"
    fields = [
        "zone", "num_inventory", "name_agent"
    ]

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "The Inventory was added.")

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
        messages.add_message(self.request, messages.SUCCESS, "Changes were saved.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("inventory_list_view")

def delete_inventory(request, pk):
    inv = Inventory.objects.get(id=pk)
    inv.delete()
    messages.success(
        request, 'Inventory deleted successfully'
    )
    return redirect(reverse('inventory_list_view'))

def get_product_data(request, pk):
    try:
        product_data = Product.objects.get(id=pk)
        json_data = serializers.serialize('json', [product_data])
        return HttpResponse(json_data, content_type='application/json')
    except Exception as er:
        print(er)
        return HttpResponse(er, content_type='application/json')
    

def ProductAutocomplete(request):
    qs = Product.objects.all()
    term = request.GET.get("term")
    if term:
        qs = qs.filter(old_ref__istartswith=term)
    data = [{"label": str(r), "id": str(r.id)} for r in qs]
    return HttpResponse(json.dumps(data), content_type='application/json')