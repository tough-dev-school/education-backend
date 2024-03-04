# Generated by Django 3.2.10 on 2022-01-01 19:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0020_OrderAuthorMigrationFix"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(("bundle__isnull", True), ("course__isnull", False), ("record__isnull", True)),
                        models.Q(("bundle__isnull", True), ("course__isnull", True), ("record__isnull", False)),
                        models.Q(("bundle__isnull", False), ("course__isnull", True), ("record__isnull", True)),
                        models.Q(("bundle__isnull", True), ("course__isnull", True), ("record__isnull", True)),
                        _connector="OR",
                    )
                ),
                name="only_one_or_zero_item_type_is_allowed",
            ),
        ),
    ]
