# Generated by Django 3.2.9 on 2022-02-28 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_phoneotp_otp_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['-updated']},
        ),
    ]
