# Generated by Django 4.2.6 on 2023-11-03 12:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studying", "0002_StudyIsHomeworkAccepted"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="study",
            options={"verbose_name": "Study", "verbose_name_plural": "Studies"},
        ),
        migrations.AlterField(
            model_name="study",
            name="course",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to="products.course", verbose_name="Course"),
        ),
        migrations.AlterField(
            model_name="study",
            name="homework_accepted",
            field=models.BooleanField(default=False, verbose_name="Homework accepted"),
        ),
        migrations.AlterField(
            model_name="study",
            name="order",
            field=models.OneToOneField(on_delete=models.deletion.CASCADE, to="orders.order", verbose_name="Order"),
        ),
        migrations.AlterField(
            model_name="study",
            name="student",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Student"),
        ),
    ]
