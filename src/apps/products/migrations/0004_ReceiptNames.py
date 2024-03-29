# Generated by Django 2.2.7 on 2019-11-08 22:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_DefaultOrdering"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="name_receipt",
            field=models.CharField(default="", max_length=255, verbose_name="Name for receipts", help_text="Will be printed in receipts"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="record",
            name="name_receipt",
            field=models.CharField(default="", max_length=255, verbose_name="Name for receipts", help_text="Will be printed in receipts"),
            preserve_default=False,
        ),
    ]
