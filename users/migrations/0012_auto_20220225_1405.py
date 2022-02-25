# Generated by Django 3.2.9 on 2022-02-25 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20220225_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='phoneotp',
            name='request_id',
            field=models.CharField(default='32453dfgdf', max_length=30, unique=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='phoneotp',
            unique_together={('phone_number', 'request_id')},
        ),
    ]
