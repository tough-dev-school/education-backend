# Generated by Django 3.2.12 on 2022-04-19 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0002_NotionaMaterialTitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='is_home_page',
            field=models.BooleanField(default=False, verbose_name='Is home page of the course'),
        ),
    ]
