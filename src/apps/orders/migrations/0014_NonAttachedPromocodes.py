# Generated by Django 3.1.7 on 2021-04-08 00:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0017_TinkoffCreditPromoCode"),
        ("orders", "0013_PerProductPromoCodes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promocode",
            name="courses",
            field=models.ManyToManyField(blank=True, help_text="Can not be used for courses not checked here", to="products.Course"),
        ),
    ]
