import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0007_membership_left_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="MembershipLeave",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.CharField(blank=True, max_length=255)),
                (
                    "membership",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_periods",
                        to="players.membership",
                    ),
                ),
            ],
            options={"ordering": ["-start_date", "-id"]},
        ),
    ]
