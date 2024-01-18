from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, CreateView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Inventory, InventoryLines
from .forms import InventoryForm, InvLinesFormSet
from django.http import HttpResponseRedirect
from django.db.models import Q
from django import forms
from django.contrib import messages



class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    context_object_name = "inventory_list" # object_list in template => book_list
    template_name = "inventory/inventory_list.html"
    ordering = ['zone', 'num_inventory']
    login_url = "account_login"


class InventoryFormView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = "inventory/inventory_detail.html"
    login_url = "account_login"
    queryset = Inventory.objects.all()

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        self.object.user = request.user
        return res


# class SearchRedictView(RedirectView):

#     def get_redirect_url(self, *args, **kwargs):
#         title = self.request.POST.get("search_input")
#         books = Book.objects.all().filter(title=title)
#         if not books:
#             return f"{reverse('book_list_view')}?not_found=1"
#         return reverse("book_form_view", args=[books[0].id])


class SearchInventoryView(ListView):
    model = Inventory
    context_object_name = "inventory_list"
    template_name = "inventory/inventory_search.html"

    def get_queryset(self) -> QuerySet[Any]:
        product_search_query = self.request.GET.get("qproduct")
        zone_search_query = self.request.GET.get("qzone")
        return self.model.objects.all().filter(
            Q(zone__name__icontains=zone_search_query) | Q(product__internal_ref__icontains=product_search_query)
        )


class InventoryInline():
    form_class = InventoryForm
    model = Inventory
    template_name = "inventory/inventory_create.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('inventory_list_view')

    def formset_lines_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        lines = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for line in lines:
            line.inventory = self.object
            line.save()


class InventoryCreate(InventoryInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(InventoryCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'lines': InvLinesFormSet(prefix='lines'),
            }
        else:
            return {
                'lines': InvLinesFormSet(self.request.POST or None, self.request.FILES or None, prefix='lines'),
            }


class InventoryUpdate(InventoryInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(InventoryUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        print("self.request.POST ::: ", self.request.POST)
        return {
            'lines': InvLinesFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='lines'),
        }

def delete_line(request, pk):
    line = InventoryLines.objects.get(id=pk)
    line.delete()
    messages.success(
            request, 'Line deleted successfully'
            )
    return reverse("inventory_update", args=[line.inventory.id])

def delete_inventory(request, pk):
    inv = Inventory.objects.get(id=pk)
    inv.delete()
    messages.success(
            request, 'Inventory deleted successfully'
            )
    return redirect('inventory_list_view')

