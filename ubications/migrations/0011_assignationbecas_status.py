# Generated by Django 5.0.3 on 2024-05-21 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ubications', '0010_alter_ubication_schedule_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignationbecas',
            name='status',
            field=models.CharField(default='candidato', max_length=50),
        ),
    ]