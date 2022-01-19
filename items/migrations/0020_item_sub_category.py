# Generated by Django 3.2.9 on 2022-01-19 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0019_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='sub_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items_included', to='items.subcategory'),
        ),
    ]