# Generated by Django 4.1.10 on 2023-08-08 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0029_DropGiftFields"),
        ("amocrm", "0003_Add_AmoCRMUserContact"),
    ]

    operations = [
        migrations.CreateModel(
            name="AmoCRMOrderTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("amocrm_id", models.PositiveIntegerField(unique=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="amocrm_transaction", to="orders.order")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AmoCRMOrderLead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("amocrm_id", models.PositiveIntegerField(unique=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="amocrm_lead", to="orders.order")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
