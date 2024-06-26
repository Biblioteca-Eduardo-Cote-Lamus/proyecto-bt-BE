# Generated by Django 5.0.3 on 2024-04-04 21:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selection', '0005_alter_selection_register_limit_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BecaTrabajo',
            fields=[
                ('code', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('direction', models.CharField(blank=True, max_length=200, null=True)),
                ('time_availability', models.CharField(blank=True, max_length=20, null=True)),
                ('shedule', models.FileField(blank=True, null=True, upload_to='')),
                ('total_hours', models.IntegerField(blank=True, default=120, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('absence', models.IntegerField(blank=True, default=0, null=True)),
                ('selection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='selection.selection')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Becas de trabajo',
                'db_table': 'becas_trabajo',
            },
        ),
    ]
