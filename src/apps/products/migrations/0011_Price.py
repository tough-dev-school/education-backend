# Generated by Django 2.2.7 on 2020-01-12 14:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0010_ParentShippableModel"),
    ]

    operations = [
        migrations.AddField(
            model_name="bundle",
            name="old_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="bundle",
            name="price",
            field=models.DecimalField(decimal_places=2, default=100500, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="course",
            name="old_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="course",
            name="price",
            field=models.DecimalField(decimal_places=2, default=100500, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="record",
            name="old_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="record",
            name="price",
            field=models.DecimalField(decimal_places=2, default=100500, max_digits=8),
            preserve_default=False,
        ),
    ]
