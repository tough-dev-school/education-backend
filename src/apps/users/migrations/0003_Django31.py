# Generated by Django 3.1.4 on 2020-12-25 20:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_SubscribedToNewsLetter"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
    ]
