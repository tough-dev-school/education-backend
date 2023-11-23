# Generated by Django 3.2.12 on 2022-03-19 09:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0002_ChainsAdminImprovements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"chain__sending_is_active": False, "children__isnull": True},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="children",
                to="chains.message",
            ),
        ),
    ]
