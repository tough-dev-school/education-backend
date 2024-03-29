# Generated by Django 4.2.5 on 2023-10-22 14:47

import django.db.models.deletion
from django.core.exceptions import ValidationError
from django.db import migrations, models
from django.db.models.fields import json


def retrieve_and_set_event_type_payment_intent(apps, schema_editor):
    del schema_editor

    StripeNotification = apps.get_model("stripebank", "StripeNotification")

    if StripeNotification.objects.exclude(raw__type="checkout.session.completed").exists():
        raise ValidationError("Only 'checkout.session.completed' events could be proceeded")

    StripeNotification.objects.update(
        event_type=json.KT("raw__type"),
        payment_intent=json.KT("raw__data__object__payment_intent"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0032_order_set_bank_choices"),
        ("stripebank", "0002_OrderUUID"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stripenotification",
            name="payment_status",
        ),
        migrations.RemoveField(
            model_name="stripenotification",
            name="status",
        ),
        migrations.AddField(
            model_name="stripenotification",
            name="event_type",
            field=models.CharField(db_index=True, default="", max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="stripenotification",
            name="payment_intent",
            field=models.CharField(db_index=True, default="", max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="stripenotification",
            name="amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AlterField(
            model_name="stripenotification",
            name="order",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="stripe_notifications", to="orders.order"),
        ),
        migrations.AlterField(
            model_name="stripenotification",
            name="payment_intent",
            field=models.CharField(db_index=True, default="", max_length=256),
        ),
        migrations.RunPython(retrieve_and_set_event_type_payment_intent),
    ]
