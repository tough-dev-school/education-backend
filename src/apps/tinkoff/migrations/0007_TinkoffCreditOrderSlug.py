# Generated by Django 3.2.13 on 2022-06-19 19:19
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
from django.db.models import F


def link_old_orders(apps, schema_editor):
    apps.get_model("tinkoff.CreditNotification").objects.update(
        order_id=F("old_order_id"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0024_OrderSlugs"),
        ("tinkoff", "0006_DolyameRefundedStatus"),
    ]

    operations = [
        migrations.RenameField(
            model_name="creditnotification",
            old_name="order_id",
            new_name="old_order_id",
        ),
        migrations.AddField(
            model_name="creditnotification",
            name="order",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to="orders.order"),
        ),
        migrations.RunPython(link_old_orders),
        migrations.AlterField(
            model_name="creditnotification",
            name="order",
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.PROTECT, to="orders.order", related_name="tinkoff_credit_notifications"),
        ),
        migrations.RemoveField(
            model_name="creditnotification",
            name="old_order_id",
        ),
    ]
