# Generated by Django 3.2.9 on 2022-02-12 06:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20220212_1220'),
        ('orders', '0002_order_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.RegexValidator(message='Only digits are allowed.', regex='^\\d*$')])),
                ('verified_phone_number', models.BooleanField(default=False)),
                ('payment_method', models.CharField(choices=[('OP', 'Online Payment'), ('COD', 'Cash On Delivery'), ('UP', 'UPI Payment')], default='OP', max_length=3)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.address')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
            options={
                'verbose_name': 'order details',
                'verbose_name_plural': 'order details',
            },
        ),
    ]
