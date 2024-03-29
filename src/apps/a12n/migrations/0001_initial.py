# Generated by Django 3.1.7 on 2021-04-04 14:54

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.a12n.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PasswordlessAuthToken",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("token", models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ("expires", models.DateTimeField(default=apps.a12n.models.default_expiration)),
                ("used", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
