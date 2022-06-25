# Generated by Django 3.2.13 on 2022-06-25 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_DiplomaTemplateContext'),
        ('mailing', '0001_EmailLogEntryMovedToDedicatedApp'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('backend', models.CharField(choices=[('', 'Unset'), ('anymail.backends.postmark.EmailBackend', 'Postmark')], default='', max_length=256)),
                ('email_from', models.CharField(help_text='E.g. Fedor Borshev <fedor@borshev.com>', max_length=256, verbose_name='Email sender')),
                ('backend_options', models.JSONField(default=dict)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='email_configuration', to='products.course')),
            ],
            options={
                'verbose_name': 'Email configuration',
                'verbose_name_plural': 'Email configurations',
            },
        ),
    ]
