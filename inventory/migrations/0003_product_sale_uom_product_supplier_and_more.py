# Generated by Django 4.0.10 on 2024-01-18 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_inventory_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sale_uom',
            field=models.CharField(choices=[('unit', 'Unité'), ('coffret', 'Coffret'), ('FL', 'FL'), ('BTE', 'Boite'), ('carton', 'Carton'), ('mc', 'MC')], default='unit', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='supplier',
            field=models.CharField(default='supplier X', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inventorylines',
            name='quantity_uom',
            field=models.CharField(choices=[('unit', 'Unité'), ('coffret', 'Coffret'), ('FL', 'FL'), ('BTE', 'Boite'), ('carton', 'Carton'), ('mc', 'MC')], default='unit', max_length=20),
        ),
    ]