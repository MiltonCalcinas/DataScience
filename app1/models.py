from django.db import models
from django.contrib.auth.models import User


class UserTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tables")
    table_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    db_name = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.user.username} - {self.table_name}"
    



class ContenidoRelacionado(models.Model):
    TIPO_CHOICES = [
        ('nota', 'Nota'),
        ('estadistica', 'Estadística'),
        ('modelo', 'Modelo Entrenado'),
        ('reporte', 'Reporte'),  # si quieres agregar también reportes
    ]

    table = models.ForeignKey(UserTable, on_delete=models.CASCADE, related_name="contenidos")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo} para {self.table.table_name}"





class Grafico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # e.g., "barra", "línea"
    datos = models.JSONField()              # valores, ejes, etc.
    posicion = models.JSONField()           # {"x": 10, "y": 20}
    tamaño = models.JSONField()             # {"width": 400, "height": 300}
    color = models.CharField(max_length=20) # "#FF5733"
    titulo = models.CharField(max_length=100)
    creado = models.DateTimeField(auto_now_add=True)
