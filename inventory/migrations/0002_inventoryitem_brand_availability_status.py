from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='availability_status',
            field=models.CharField(choices=[('available', 'Available'), ('missing', 'Missing'), ('destroyed', 'Destroyed'), ('distributed', 'Distributed')], default='available', max_length=20),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='brand',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
