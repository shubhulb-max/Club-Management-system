from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0005_membership_fee_exempt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="role",
            field=models.CharField(
                choices=[
                    ("top_order_batter", "Top-order batter"),
                    ("middle_order_batter", "Middle-order batter"),
                    ("wicket_keeper_batter", "Wicket-keeper batter"),
                    ("wicket_keeper", "Wicket-keeper"),
                    ("bowler", "Bowler"),
                    ("all_rounder", "All-Rounder"),
                    ("lower_order_batter", "Lower-order batter"),
                    ("opening_batter", "Opening batter"),
                    ("none", "None"),
                ],
                default="all_rounder",
                max_length=30,
            ),
        ),
    ]
