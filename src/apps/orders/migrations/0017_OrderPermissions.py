# Generated by Django 3.2.8 on 2021-10-28 16:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0016_UnpaidDate"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={
                "ordering": ["-id"],
                "permissions": [("pay_order", "May mark orders as paid"), ("unpay_order", "May mark orders as unpaid")],
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),
    ]
