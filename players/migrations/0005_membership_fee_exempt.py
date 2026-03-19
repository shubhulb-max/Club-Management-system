from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0004_registrationrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="fee_exempt",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="membership",
            name="fee_exempt_reason",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
