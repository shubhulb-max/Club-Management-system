from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0004_alter_match_ball_type"),
        ("players", "0003_alter_player_age_alter_player_first_name_and_more"),
        ("teams", "0002_alter_team_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lineup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_lineups", to="players.player")),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineups", to="matches.match")),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineups", to="teams.team")),
            ],
            options={
                "unique_together": {("match", "team")},
            },
        ),
        migrations.CreateModel(
            name="LineupEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("batting_order", models.PositiveSmallIntegerField()),
                ("role", models.CharField(max_length=30)),
                ("is_captain", models.BooleanField(default=False)),
                ("is_wicket_keeper", models.BooleanField(default=False)),
                ("is_substitute", models.BooleanField(default=False)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
                ("lineup", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="entries", to="matches.lineup")),
                ("player", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineup_entries", to="players.player")),
            ],
            options={
                "unique_together": {("lineup", "batting_order"), ("lineup", "player")},
            },
        ),
    ]
