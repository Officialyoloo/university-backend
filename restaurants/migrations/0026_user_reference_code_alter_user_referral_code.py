# Generated by Django 4.0.5 on 2022-06-26 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0025_alter_paytmorder_order_schedule_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reference_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.CharField(max_length=10),
        ),
    ]
