# Generated by Django 2.2.13 on 2020-09-30 13:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_PromoCodesActiveByDefault"),
    ]

    operations = [
        migrations.AddField(
            model_name="promocode",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
    ]
