from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.

from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Los superusuarios deben tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Los superusuarios deben tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Rol(models.Model):
    descripcion = models.CharField(max_length=100)
    class Meta:
        db_table = "roles"

# Modificamos la clase de autenticación de usuario de django para que el usuario se autentique con el email
class Usuario(AbstractUser):
    
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, null=True, blank=True)

    objects = UsuarioManager()

    class Meta:
        #cambiamos el nombre de la tabla para mejor entendimiento
        db_table = "usuarios"


