# Generated by Django 3.2.12 on 2022-04-05 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_InternationalNames'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='mailchimp_list_id',
        ),
        migrations.AddField(
            model_name='course',
            name='dashamail_list_id',
            field=models.CharField(blank=True, help_text='Get it from audience settings', max_length=32, null=True, verbose_name='Dashamail audience id'),
        ),
    ]
