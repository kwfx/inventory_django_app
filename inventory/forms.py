from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, CreateView
from django.contrib.auth import get_user_model
from .models import Inventory, InventoryLines
from django.http import HttpResponseRedirect
from django.db.models import Q
from django import forms
from django.contrib.admin.widgets import AdminDateWidget


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = '__all__'


class InventoryLineForm(forms.ModelForm):
    class Meta:
        model = InventoryLines
        fields = '__all__'
        widgets = {
            'expiration_date': forms.TextInput(attrs={'type': 'date'}),
        }


InvLinesFormSet = forms.inlineformset_factory(
    Inventory, InventoryLines, form=InventoryLineForm,
    extra=1, can_delete=True, can_delete_extra=True
)

