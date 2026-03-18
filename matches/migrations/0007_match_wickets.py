from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0006_match_format_and_result_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="team1_wickets",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="team2_wickets",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
