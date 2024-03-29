# Generated by Django 2.2.13 on 2020-09-30 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_OrderPromoCodes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="promocode",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="orders.PromoCode", verbose_name="Promo Code"),
        ),
        migrations.AlterField(
            model_name="promocode",
            name="active",
            field=models.BooleanField(default=True, verbose_name="Active"),
        ),
        migrations.AlterField(
            model_name="promocode",
            name="comment",
            field=models.TextField(blank=True, null=True, verbose_name="Comment"),
        ),
    ]
