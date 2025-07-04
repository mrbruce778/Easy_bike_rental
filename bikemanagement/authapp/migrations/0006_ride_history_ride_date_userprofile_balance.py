# Generated by Django 4.2.21 on 2025-05-14 14:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0005_remove_bike_station_id_bike_current_station'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride_history',
            name='ride_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=500.0, max_digits=10),
        ),
    ]
