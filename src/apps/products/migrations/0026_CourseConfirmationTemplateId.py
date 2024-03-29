# Generated by Django 3.2.15 on 2022-09-21 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0025_DisableTriggersFlag"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="confirmation_template_id",
            field=models.CharField(
                blank=True,
                help_text="If set user sill receive this message upon creating zero-priced order",
                max_length=255,
                null=True,
                verbose_name="Confirmation template id",
            ),
        ),
    ]
