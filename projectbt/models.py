# We create this general models.py file to store all the models for the project.
# This is a good practice to keep the project organized and clean.
# We can also create a models.py file for each app, but for this project, we will use a general models.py file.

# Path: projectbt/models.py
from django.db import models

# Create your models here.


class BecaTrabajo(models.Model):
    codigo = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Código",
        help_text="Código del becatrabajo",
        null=False,
        blank=False,
        primary_key=True,
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre del becatrabajo",
        null=False,
        blank=False,
    )

    apellido = models.CharField(
        max_length=100,
        verbose_name="Apellido",
        help_text="Apellido del becatrabajo",
        null=False,
        blank=True,
    )

    horas_totales = models.IntegerField(
        verbose_name="Horas totales",
        help_text="Horas totales del becatrabajo",
        null=False,
        blank=False,
        default=140,
    )

    horas_realizadas = models.IntegerField(
        verbose_name="Horas realizadas",
        help_text="Horas realizadas del becatrabajo",
        null=False,
        blank=False,
        default=0,
    )

    inasistencias = models.IntegerField(
        verbose_name="Inasistencias",
        help_text="Inasistencias del becatrabajo",
        null=False,
        blank=False,
        default=0,
    )

    # haz una llave foranea con la tabla User del modelo auth de django
    usuario = models.ForeignKey(
        "auth.User",
        verbose_name="Usuario",
        help_text="Usuario del becatrabajo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Beca Trabajo"
        verbose_name_plural = "Becas Trabajo"
        db_table = "becatrabajo"
