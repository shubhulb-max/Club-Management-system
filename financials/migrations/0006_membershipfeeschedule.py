from decimal import Decimal

from django.db import migrations, models


def seed_membership_fee_schedule(apps, schema_editor):
    MembershipFeeSchedule = apps.get_model("financials", "MembershipFeeSchedule")
    MembershipFeeSchedule.objects.update_or_create(
        effective_from="2025-01-01",
        defaults={"amount": Decimal("750.00")},
    )
    MembershipFeeSchedule.objects.update_or_create(
        effective_from="2026-01-01",
        defaults={"amount": Decimal("1050.00")},
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("financials", "0005_alter_transaction_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="MembershipFeeSchedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("effective_from", models.DateField(unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={"ordering": ["-effective_from"]},
        ),
        migrations.RunPython(seed_membership_fee_schedule, noop),
    ]
