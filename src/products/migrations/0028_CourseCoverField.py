# Generated by Django 3.2.16 on 2022-12-27 21:34

import app.files
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_CourseConfirmationURL'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='cover',
            field=models.ImageField(blank=True, help_text='The cover image of course', upload_to=app.files.RandomFileName('courses/covers'), verbose_name='Cover image'),
        ),
    ]