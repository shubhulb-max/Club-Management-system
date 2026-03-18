from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0008_match_type_and_tournament"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="status",
            field=models.CharField(
                choices=[
                    ("scheduled", "Scheduled"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="scheduled",
                max_length=20,
            ),
        ),
    ]
