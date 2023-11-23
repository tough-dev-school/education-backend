# Generated by Django 3.1.8 on 2021-04-26 21:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0017_TinkoffCreditPromoCode"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=256)),
            ],
            options={
                "verbose_name": "Analytical group",
                "verbose_name_plural": "Analytical groups",
            },
        ),
        migrations.AddField(
            model_name="bundle",
            name="group",
            field=models.ForeignKey(null=True, blank=True, verbose_name="Analytical group", on_delete=django.db.models.deletion.SET_NULL, to="products.group"),
        ),
        migrations.AddField(
            model_name="course",
            name="group",
            field=models.ForeignKey(null=True, blank=True, verbose_name="Analytical group", on_delete=django.db.models.deletion.SET_NULL, to="products.group"),
        ),
        migrations.AddField(
            model_name="record",
            name="group",
            field=models.ForeignKey(null=True, blank=True, verbose_name="Analytical group", on_delete=django.db.models.deletion.SET_NULL, to="products.group"),
        ),
    ]
