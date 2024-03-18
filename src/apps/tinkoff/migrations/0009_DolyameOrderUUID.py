# Generated by Django 3.2.13 on 2022-06-22 20:36
import django.db.models.deletion
from django.db import migrations, models
from django.db.models import F, Value
from django.db.models.functions import Cast, Replace


def link_old_orders(apps, schema_editor):
    del schema_editor

    apps.get_model("tinkoff.DolyameNotification").objects.update(
        order_id=Cast(
            Replace(F("old_order_id"), Value("tds-"), Value("")),
            output_field=models.IntegerField(),
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0024_OrderSlugs"),
        ("tinkoff", "0008_TinkoffBankOrderSlug"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dolyamenotification",
            old_name="order_id",
            new_name="old_order_id",
        ),
        migrations.AddField(
            model_name="dolyamenotification",
            name="order",
            field=models.ForeignKey(to="orders.Order", null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.RunPython(link_old_orders),
        migrations.AlterField(
            model_name="dolyamenotification",
            name="order",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="dolyame_notifications", to="orders.order"),
        ),
        migrations.RemoveField(
            model_name="dolyamenotification",
            name="old_order_id",
        ),
    ]
