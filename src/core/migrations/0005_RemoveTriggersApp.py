# Generated by Django 4.1.7 on 2023-05-07 18:00

from django.db import migrations


def remove_contenttypes(apps, schema_editor):
    apps.get_model("contenttypes.ContentType").objects.filter(app_label="triggers").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_EmailLogEntryMovedToDedicatedApp"),
    ]

    operations = [
        migrations.RunPython(remove_contenttypes),
        migrations.RunSQL("DROP TABLE IF EXISTS triggers_triggerlogentry"),
    ]
