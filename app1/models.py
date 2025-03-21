from django.db import models

# Create your models here.
class TablaUsuario(models.Model):
    usuario = models.CharField(max_length=150, unique=True)
    nombre_tabla = models.CharField(max_length=255)