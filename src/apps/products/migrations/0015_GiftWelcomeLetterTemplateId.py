# Generated by Django 3.1.4 on 2020-12-31 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0014_CourseWelcomeLetter"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="gift_welcome_letter_template_id",
            field=models.CharField(
                blank=True,
                help_text="If not set, common welcome letter will be used",
                max_length=255,
                null=True,
                verbose_name="Special welcome letter template id for gifts",
            ),
        ),
    ]
