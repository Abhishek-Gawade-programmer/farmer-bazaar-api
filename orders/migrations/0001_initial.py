# Generated by Django 3.2.9 on 2022-01-20 14:12

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed', models.DateTimeField(blank=True, null=True)),
                ('paid', models.DateTimeField(blank=True, null=True)),
                ('dispatched', models.DateTimeField(blank=True, null=True)),
                ('delivered', models.DateTimeField(blank=True, null=True)),
                ('rejected', models.DateTimeField(blank=True, null=True)),
                ('reject_reason', models.TextField(blank=True, max_length=1000)),
                ('current_order', models.BooleanField(blank=True, default=False, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('item_bag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='active_orders', to='items.itembag')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.order')),
            ],
        ),
    ]
