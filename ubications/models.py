from django.db import models
from authApi.models import Usuario

class ScheduleType(models.Model):
    # nombre del tipo de horario que sea unico
    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    class Meta:
        db_table = 'tipos_de_horarios'

class Ubication(models.Model):

    def photo_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
        return 'ubications/{0}/{1}/{2}'.format(instance.name, 'fotos', filename) 

    # nombre de la ubicacion
    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    # encargado de la ubicacion
    manager = models.ForeignKey(Usuario,on_delete=models.SET_NULL, null=True)
    # cantidad de becas que se pueden asignar
    total_becas = models.IntegerField(blank=False, null=False)
    # Descripcion de la ubicacion 
    description = models.CharField(max_length=150,blank=True, null=True)
    # Imagen de la ubicacion para reconocerla 
    img = models.ImageField(upload_to=photo_path, blank=True, null=True)
    # Tipo de horario que se maneja en la ubicacion (Valores: Unificado exluyendo sabado, unificado incluyendo sabado, personalizado)
    schedule_type = models.ForeignKey(ScheduleType, on_delete=models.SET_NULL, null=True)
        
    class Meta:
        db_table = 'ubicaciones'

# Modelo para representar los horarios de las ubicaciones
class Schedule(models.Model):
    # ubicacion a la que pertenece el horario
    ubication = models.ForeignKey(Ubication, on_delete=models.SET_NULL, related_name='schedules', null=True, blank=True)
    # hora de inicio del horario
    start_hour = models.CharField(max_length=10)
    # hora de fin del horario
    end_hour = models.CharField(max_length=10)
    # Dia de la semana en el que se aplica el horario (Valores: Lunes, Martes, Miercoles, Jueves, Viernes, Sabado)
    days = models.CharField(max_length=60)
    # Cantidad de becas que se pueden asignar en este horario
    total_becas = models.IntegerField(blank=False, null=False, default=1)
    # Campo para guardar un json en caso de que el horario sea personalizado
    becas_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'horarios_por_ubicacion'
        # Se define que la combinacion de ubicacion, hora de inicio y hora de fin debe ser unica
        unique_together = ('ubication', 'start_hour', 'end_hour', 'days')

# Modelo para representar las asignaciones de becas a horarios
class AssignationBecas(models.Model):
    # beca que se asigna al horario
    beca = models.ForeignKey('selection.BecaTrabajo', on_delete=models.SET_NULL, related_name='assignations', null=True, blank=True)
    # horario al que se asigna la beca
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, related_name='assignations', null=True, blank=True)

    class Meta:
        db_table = 'asignaciones_de_becas'
        # Se define que la combinacion de beca y horario debe ser unica
        unique_together = ('beca', 'schedule')

class ScheduleFormat(models.Model):
    schedule = models.JSONField(blank=False, null=False)
    ubication = models.OneToOneField(Ubication, on_delete=models.SET_NULL, related_name='schedule_format', null=True, blank=True)

    class Meta:
        db_table = 'formato_de_horarios'