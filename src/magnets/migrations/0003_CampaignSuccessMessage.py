# Generated by Django 2.2.13 on 2020-10-06 18:24

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('magnets', '0002_CampaignLog'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailleadmagnetcampaign',
            name='success_message',
            field=models.CharField(default='', help_text='Will be shown under tilda form', max_length=255, verbose_name='Success Message'),
            preserve_default=False,
        ),
    ]
