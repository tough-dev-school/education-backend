# Generated by Django 4.1.9 on 2023-07-07 07:54

import django_jsonform.models.fields

import django.contrib.postgres.indexes
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_drop_linkedin_github_constraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="tags",
            field=django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=512), default=list, size=None),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.GinIndex(fields=["tags"], name="users_user_tags_d41b16_gin"),
        ),
    ]
