# Generated by Django 4.1.9 on 2023-07-07 12:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0029_TagsForUser"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bundle",
            name="slug",
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name="record",
            name="slug",
            field=models.SlugField(unique=True),
        ),
    ]
