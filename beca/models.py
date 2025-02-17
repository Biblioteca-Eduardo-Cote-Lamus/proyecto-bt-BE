from django.db import models

class Beca(models.Model):
    code = models.CharField(
        max_length=15, 
        unique=True, 
        primary_key=True,
        verbose_name="Código"
    )
    first_name = models.CharField(max_length=100, verbose_name="Nombre", null=True)
    last_name = models.CharField(max_length=100, verbose_name="Apellido", null=True)
    photo = models.ImageField(
        upload_to='becas/', 
        null=True, 
        blank=True,
        verbose_name="Foto"
    )
    ubication = models.ForeignKey(
        'ubications.Ubication', 
        on_delete=models.CASCADE,
        verbose_name="Ubicación"
    )
    selection = models.ForeignKey(
        'Selection', 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name="Selección"
    )

    class Meta:
        db_table = 'becas'
        verbose_name = "Beca"
        verbose_name_plural = "Becas"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.code})"

class BecaSchedule(models.Model):
    beca = models.ForeignKey(
        Beca, 
        related_name='beca_schedules', 
        on_delete=models.CASCADE
    )
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'beca_schedules'

class Selection(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre del periodo de selección"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si la selección está activa"
    )

    class Meta:
        db_table = 'selections'