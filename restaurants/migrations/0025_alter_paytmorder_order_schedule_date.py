# Generated by Django 4.0.5 on 2022-06-26 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0024_alter_menuitems_food_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paytmorder',
            name='order_schedule_date',
            field=models.DateTimeField(),
        ),
    ]
