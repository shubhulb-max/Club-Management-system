from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0007_match_wickets"),
        ("tournaments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="match_type",
            field=models.CharField(
                choices=[("friendly", "Friendly"), ("tournament", "Tournament")],
                default="friendly",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="tournament",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="matches",
                to="tournaments.tournament",
            ),
        ),
    ]
