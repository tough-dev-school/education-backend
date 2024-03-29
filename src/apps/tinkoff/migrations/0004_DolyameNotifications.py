# Generated by Django 3.2.12 on 2022-04-29 19:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tinkoff", "0003_CreditNotifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="DolyameNotification",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("order_id", models.CharField(max_length=256)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("canceled", "Canceled"),
                            ("commited", "Commited"),
                            ("wait_for_commit", "Waiting for commit"),
                            ("completed", "Completed"),
                        ],
                        max_length=32,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("demo", models.BooleanField()),
                ("residual_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("client_info", models.JSONField(default=dict)),
                ("payment_schedule", models.JSONField(default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
