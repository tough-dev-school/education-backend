# Generated by Django 3.1.8 on 2021-05-02 12:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0009_ExcludeAnswersFromCrossCheck'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='modified',
            field=models.DateTimeField(auto_now=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
