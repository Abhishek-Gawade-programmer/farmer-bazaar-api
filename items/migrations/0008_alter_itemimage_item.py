# Generated by Django 3.2.9 on 2021-12-28 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_item_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemimage',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='items.item'),
        ),
    ]
