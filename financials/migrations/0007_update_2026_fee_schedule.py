from decimal import Decimal

from django.db import migrations


def update_2026_fee_schedule(apps, schema_editor):
    MembershipFeeSchedule = apps.get_model("financials", "MembershipFeeSchedule")
    MembershipFeeSchedule.objects.filter(effective_from="2026-01-01").delete()
    MembershipFeeSchedule.objects.update_or_create(
        effective_from="2026-02-01",
        defaults={"amount": Decimal("1050.00")},
    )


def revert_2026_fee_schedule(apps, schema_editor):
    MembershipFeeSchedule = apps.get_model("financials", "MembershipFeeSchedule")
    MembershipFeeSchedule.objects.filter(effective_from="2026-02-01").delete()
    MembershipFeeSchedule.objects.update_or_create(
        effective_from="2026-01-01",
        defaults={"amount": Decimal("1050.00")},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("financials", "0006_membershipfeeschedule"),
    ]

    operations = [
        migrations.RunPython(update_2026_fee_schedule, revert_2026_fee_schedule),
    ]
