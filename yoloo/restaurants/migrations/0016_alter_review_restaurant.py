# Generated by Django 4.0.5 on 2022-06-22 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0015_paytmorder_order_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurants.restaurant'),
        ),
    ]
