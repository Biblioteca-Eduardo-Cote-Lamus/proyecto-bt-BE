# Generated by Django 5.0.3 on 2024-05-13 01:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ubications', '0008_scheduleformat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleformat',
            name='ubication',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_format', to='ubications.ubication'),
        ),
    ]