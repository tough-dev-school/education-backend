# Generated by Django 4.2.20 on 2025-04-04 16:39

from typing import no_type_check

import django.db.models.deletion
from django.db import migrations, models

import core.models


@no_type_check
def migrate_lessons_to_modules(apps, schema_editor):  # NOQA: ARG001
    Lesson = apps.get_model("lessons.Lesson")
    Module = apps.get_model("lessons.Module")

    for lesson in Lesson.objects.all():
        module = Module.objects.create(
            name=lesson.name,
            course=lesson.course,
            position=lesson.position,
            hidden=lesson.hidden,
        )
        lesson.module = module
        lesson.save()


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0002_homework"),
    ]

    operations = [
        migrations.CreateModel(
            name="Module",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="modules", to="lessons.lessoncourse")),
                ("hidden", models.BooleanField(default=True, help_text="Users can't find such materials in the listing", verbose_name="Hidden")),
                ("position", models.PositiveIntegerField(db_index=True, default=0)),
            ],
            options={
                "ordering": ["position"],
            },
            bases=(core.models.TestUtilsMixin, models.Model),
        ),
        migrations.AddField(
            model_name="lesson",
            name="module",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="lessons.module", verbose_name="Module"),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_lessons_to_modules),
        migrations.AlterField(
            model_name="lesson",
            name="module",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="lessons.module", verbose_name="Module"),
            preserve_default=False,
        ),
        migrations.RemoveIndex(
            model_name="lesson",
            name="lessons_les_course__6bd811_idx",
        ),
        migrations.RemoveField(
            model_name="lesson",
            name="course",
        ),
        migrations.AddIndex(
            model_name="lesson",
            index=models.Index(fields=["module", "position"], name="lessons_les_module__7e7bac_idx"),
        ),
        migrations.AddIndex(
            model_name="module",
            index=models.Index(fields=["course", "position"], name="lessons_mod_course__887acb_idx"),
        ),
    ]
