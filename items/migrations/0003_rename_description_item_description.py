# Generated by Django 3.2.9 on 2021-12-25 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_auto_20211225_1542'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='Description',
            new_name='description',
        ),
    ]