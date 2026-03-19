from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financials", "0007_update_2026_fee_schedule"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="waived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="transaction",
            name="waived_reason",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
