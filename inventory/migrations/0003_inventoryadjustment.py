from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_inventoryitem_brand_availability_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjustment_type', models.CharField(choices=[('addition', 'Addition'), ('missing', 'Marked Missing'), ('destroyed', 'Destroyed'), ('distributed', 'Distributed')], max_length=20)),
                ('quantity', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjustments', to='inventory.inventoryitem')),
            ],
        ),
    ]
