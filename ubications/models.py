from django.db import models
from authApi.models import Usuario
# Create your models here.
class HourSchedule(models.Model):

    tiempo = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'horas_horario'


class Ubication(models.Model):

    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    total_becas = models.IntegerField(blank=False, null=False)
    manager = models.ForeignKey(Usuario,on_delete=models.SET_NULL, null=True)
    is_schedule_office = models.BooleanField(verbose_name='es horario de oficina', default=True, blank=False, null=True)
    schedule = models.ManyToManyField(HourSchedule)

    class Meta:
        db_table = 'ubicaciones'