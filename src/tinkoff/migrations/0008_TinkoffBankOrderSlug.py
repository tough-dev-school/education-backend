# Generated by Django 3.2.13 on 2022-06-19 19:32

from django.db import migrations
from django.db import models
from django.db.models import F
import django.db.models.deletion


def remove_orphan_transactions(apps, schema_editor):
    apps.get_model('tinkoff.PaymentNotification').objects.filter(
        old_order_id__in=[948, 1153, 1166, 1167],
    ).delete()


def link_old_orders(apps, schema_editor):
    apps.get_model('tinkoff.PaymentNotification').objects.update(
        order_id=F('old_order_id'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0024_OrderSlugs'),
        ('tinkoff', '0007_TinkoffCreditOrderSlug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentnotification',
            old_name='order_id',
            new_name='old_order_id',
        ),
        migrations.AddField(
            model_name='paymentnotification',
            name='order',
            field=models.ForeignKey(null=True, to='orders.Order', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.RunPython(remove_orphan_transactions),
        migrations.RunPython(link_old_orders),
        migrations.AlterField(
            model_name='paymentnotification',
            name='order',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.PROTECT, related_name='tinkoff_payment_notifications', to='orders.order'),
        ),
        migrations.RemoveField(
            model_name='paymentnotification',
            name='old_order_id',
        ),
    ]
