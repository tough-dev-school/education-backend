# Generated by Django 3.1.4 on 2020-12-31 21:27

from django.db import migrations, models


def mark_giver_notification_as_sent_for_all_previous_orders(apps, schema_editor):
    apps.get_model("orders.Order").objects.filter(giver__isnull=False).update(notification_to_giver_is_sent=True)


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0010_OrderI18n"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="notification_to_giver_is_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_giver_notification_as_sent_for_all_previous_orders),
    ]
