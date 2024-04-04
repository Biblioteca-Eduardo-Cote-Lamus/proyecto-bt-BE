from django.db import models

class SelectionState(models.Model):
    state = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        db_table = 'estado_seleccion'
        verbose_name = 'Estado de selección'
        verbose_name_plural = 'Estados del proceso de selección'

# Create your models here.
class Selection(models.Model):
    semester = models.CharField(max_length=100, blank=True, null=True)
    current_state = models.ForeignKey(SelectionState, on_delete=models.CASCADE, blank=True, null=True)
    register_limit_date = models.DateTimeField(blank=True, null=True)
    selection_start_date = models.DateTimeField(blank=True, null=True)
    selection_end_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    class Meta:
        db_table = 'seleccion'
        verbose_name = 'Selección'
        verbose_name_plural = 'Selecciones'