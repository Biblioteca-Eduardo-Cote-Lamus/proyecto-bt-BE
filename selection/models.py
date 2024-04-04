from django.db import models


class SelectionState(models.Model):
    state = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "estado_seleccion"
        verbose_name = "Estado de selección"
        verbose_name_plural = "Estados del proceso de selección"


# Create your models here.
class Selection(models.Model):
    semester = models.CharField(max_length=100, blank=True, null=True)
    current_state = models.ForeignKey(
        SelectionState, on_delete=models.CASCADE, blank=True, null=True
    )
    register_limit_date = models.DateTimeField(blank=True, null=True)
    selection_start_date = models.DateTimeField(blank=True, null=True)
    selection_end_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    class Meta:
        db_table = "seleccion"
        verbose_name = "Selección"
        verbose_name_plural = "Selecciones"


class BecaTrabajo(models.Model):
    # Foreing key to selection
    selection = models.ForeignKey(
        Selection, on_delete=models.CASCADE, blank=True, null=True
    )
    student = models.OneToOneField(
        "authApi.Usuario", on_delete=models.CASCADE, blank=True, null=True
    )

    # Fields

    code = models.CharField(max_length=100, blank=False, null=False, primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(blank=True, null=True)
    direction = models.CharField(max_length=200, blank=True, null=True)
    time_availability = models.CharField(max_length=20, blank=True, null=True)
    shedule = models.FileField(blank=True, null=True)
    total_hours = models.IntegerField(blank=True, null=True, default=120)
    is_active = models.BooleanField(default=True)
    absence = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = "becas_trabajo"
        verbose_name = "Becas de trabajo"
