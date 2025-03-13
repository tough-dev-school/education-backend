# Generated by Django 4.2.20 on 2025-03-09 19:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import core.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0033_ProductGroupDashamail"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=255, verbose_name="Customer name")),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
            },
            bases=(core.models.TestUtilsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Deal",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("comment", models.TextField(blank=True, verbose_name="Comment")),
                ("completed", models.DateTimeField(blank=True, null=True, verbose_name="Date when the deal got completed")),
                ("canceled", models.DateTimeField(blank=True, null=True, verbose_name="Date when the deal got canceled")),
                ("shipped_without_payment", models.DateTimeField(blank=True, null=True, verbose_name="Date when the deal got shipped without payment")),
                ("price", models.DecimalField(decimal_places=2, max_digits=9, verbose_name="Price")),
                (
                    "author",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_deals",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Deal author",
                    ),
                ),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="products.course")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="b2b.customer", verbose_name="Customer")),
            ],
            options={
                "verbose_name": "Deal",
                "verbose_name_plural": "Deals",
            },
            bases=(core.models.TestUtilsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("deal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="students", to="b2b.deal")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Student",
                "verbose_name_plural": "Students",
            },
            bases=(core.models.TestUtilsMixin, models.Model),
        ),
    ]
