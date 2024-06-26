# Generated by Django 5.0.3 on 2024-04-11 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selection', '0008_alter_becatrabajo_selection_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='becatrabajo',
            old_name='direction',
            new_name='address',
        ),
        migrations.RemoveField(
            model_name='becatrabajo',
            name='shedule',
        ),
        migrations.RemoveField(
            model_name='becatrabajo',
            name='time_availability',
        ),
        migrations.AddField(
            model_name='becatrabajo',
            name='career',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='becatrabajo',
            name='gender',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='becatrabajo',
            name='schedule',
            field=models.FileField(blank=True, null=True, upload_to='horarios'),
        ),
        migrations.AlterField(
            model_name='becatrabajo',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='fotos'),
        ),
    ]
