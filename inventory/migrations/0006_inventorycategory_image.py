from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_inventorycategory_inventoryitem_available_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorycategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='inventory/categories/'),
        ),
    ]
