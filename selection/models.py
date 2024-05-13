from django.db import models
from ubications.models import Ubication
class SelectionState(models.Model):
    state = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "estado_seleccion"
        verbose_name = "Estado de selección"
        verbose_name_plural = "Estados del proceso de selección"

class BecaState(models.Model):
    state = models.CharField(max_length=50,blank=True, null=True)

    class Meta:
        db_table = "estado_beca"
        verbose_name = "Estado actual del beca"

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
    total_becas = models.IntegerField(default=16, blank=True, null=True)

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

    current_state = models.ForeignKey(
        BecaState, on_delete=models.CASCADE, blank=True, null=True
    )

    ubication = models.ForeignKey(Ubication, on_delete=models.SET_NULL, null=True, blank=True)

    def photo_path(instance, filename): 
        # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
        return 'becas-trabajo/{0}/{1}/{2}'.format(instance.code, 'fotos', filename) 
    
    def schedule_path(instance, filename): 
        # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
        return 'becas-trabajo/{0}/{1}/{2}'.format(instance.code, 'horario', filename) 

    # Fields

    code = models.CharField(max_length=100, blank=False, null=False, primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(blank=True, null=True, upload_to=photo_path)
    address = models.CharField(max_length=200, blank=True, null=True)
    schedule = models.FileField(blank=True, null=True, upload_to=schedule_path)
    total_hours = models.IntegerField(blank=True, null=True, default=120)
    is_active = models.BooleanField(default=True)
    absence = models.IntegerField(blank=True, null=True, default=0)
    gender = models.CharField(max_length=25, blank=True, null=True)
    career = models.CharField(max_length=100, blank=True, null=True)
    extra_studies = models.TextField(blank=True, null=True)
    motivation = models.TextField(blank=True, null=True)
    sended_form = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        db_table = "becas_trabajo"
        verbose_name = "Becas de trabajo"
