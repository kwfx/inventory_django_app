# Generated by Django 4.0.10 on 2024-01-20 11:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_inventorylines_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorylines',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2024, 1, 20, 12, 34, 1, 769564), verbose_name='Date péremption'),
        ),
    ]
