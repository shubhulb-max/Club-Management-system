from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0006_alter_player_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="membership",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("inactive", "Inactive"),
                    ("pending", "Pending"),
                    ("left", "Left Club"),
                ],
                default="pending",
                max_length=10,
            ),
        ),
    ]
