from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0005_lineup_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="match_format",
            field=models.CharField(
                blank=True,
                choices=[
                    ("t10", "T10"),
                    ("t20", "T20"),
                    ("odi", "ODI"),
                    ("test", "Test"),
                    ("other", "Other"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="overs_per_side",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="team1_overs",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="team1_runs",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="team2_overs",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="team2_runs",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
