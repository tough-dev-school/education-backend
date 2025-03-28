# Generated by Django 4.2.20 on 2025-03-22 14:43

from django.db import migrations, models

import core.models


class Migration(migrations.Migration):
    dependencies = [
        ("notion", "0013_video_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("source", models.CharField(db_index=True, max_length=64, verbose_name="Source page notion id")),
                ("destination", models.CharField(db_index=True, max_length=64, verbose_name="Destination page notion id")),
            ],
            options={
                "indexes": [models.Index(fields=["source", "destination"], name="notion_page_source_67a8c5_idx")],
            },
            bases=(core.models.TestUtilsMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name="pagelink",
            constraint=models.UniqueConstraint(fields=("source", "destination"), name="unique_link_pair"),
        ),
    ]
