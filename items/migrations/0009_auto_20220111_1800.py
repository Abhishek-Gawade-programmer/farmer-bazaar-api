# Generated by Django 3.2.9 on 2022-01-11 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0008_alter_itemimage_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='location',
        ),
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(choices=[('blue', 'primary'), ('purple', 'secondary'), ('red', 'danger'), ('lightblue', 'info'), ('yellow', 'warning'), ('black', 'dark'), ('default', 'default')], default='default', max_length=9),
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(null=True, upload_to='category_images/'),
        ),
    ]