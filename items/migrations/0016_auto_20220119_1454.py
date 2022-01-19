# Generated by Django 3.2.9 on 2022-01-19 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0015_itembag'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itembag',
            options={'ordering': ('item',)},
        ),
        migrations.AlterUniqueTogether(
            name='itembag',
            unique_together={('item', 'quantity', 'quantity_unit')},
        ),
    ]
