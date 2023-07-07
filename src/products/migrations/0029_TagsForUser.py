# Generated by Django 4.1.9 on 2023-07-07 06:54

from django.db import migrations
from django.db import models


def set_default_slug_to_group(apps, schema_editor):
    Group = apps.get_model("products", "Group")
    Course = apps.get_model("products", "Course")
    groups = Group.objects.all()

    def get_product_group_slug(group):
        first_course = Course.objects.filter(group=group).first()
        return '-'.join(first_course.slug.split('-')[:-1])

    for group in groups:
        group.slug = get_product_group_slug(group)
        group.save()


def revert_set_default_slug_to_group(apps, schema_editor):
    Group = apps.get_model("products", "Group")
    Group.objects.update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0028_CourseCoverField"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="slug",
            field=models.SlugField(null=True),
        ),
        migrations.RunPython(set_default_slug_to_group, reverse_code=revert_set_default_slug_to_group),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(null=False)
        ),
    ]
