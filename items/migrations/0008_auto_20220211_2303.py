# Generated by Django 3.2.9 on 2022-02-11 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_auto_20220211_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subcategory',
            name='color',
        ),
        migrations.RemoveField(
            model_name='subcategory',
            name='user',
        ),
    ]
