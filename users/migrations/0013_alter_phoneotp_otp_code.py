# Generated by Django 3.2.9 on 2022-02-25 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20220225_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phoneotp',
            name='otp_code',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
