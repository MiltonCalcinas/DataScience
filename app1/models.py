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





# class Grafico(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE)
#     tipo = models.CharField(max_length=50)  # e.g., "barra", "línea"
#     datos = models.JSONField()              # valores, ejes, etc.
#     posicion = models.JSONField()           # {"x": 10, "y": 20}
#     tamaño = models.JSONField()             # {"width": 400, "height": 300}
#     color = models.CharField(max_length=20) # "#FF5733"
#     titulo = models.CharField(max_length=100)
#     creado = models.DateTimeField(auto_now_add=True)


from django.db import models

class TextBox(models.Model):
    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    contenedor_nombre = models.CharField(max_length=100)
    contenedor_pestana = models.CharField(max_length=100)
    contenedor_x = models.IntegerField()
    contenedor_y = models.IntegerField()
    contenedor_ancho = models.IntegerField()
    contenedor_alto = models.IntegerField()
    color_frame = models.CharField(max_length=7)
    borde_redondeado = models.IntegerField()
    textbox_contenido = models.TextField()
    textbox_negrita = models.BooleanField()
    textbox_tamaño_letra = models.IntegerField()
    textbox_capitalizado = models.BooleanField()
    textbox_underline = models.BooleanField()
    textbox_fuente = models.CharField(max_length=100)
    textbox_color = models.CharField(max_length=7, default="#000000")  # Por ejemplo, negro
    textbox_fondo_color = models.CharField(max_length=7,default='#ffffff')
    def __str__(self):
        return f"{self.contenedor_nombre} en {self.contenedor_pestana}"



class Grafico(models.Model):
    table = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    contenedor_nombre = models.CharField(max_length=100)
    contenedor_pestana = models.CharField(max_length=100)
    contenedor_x = models.IntegerField()
    contenedor_y = models.IntegerField()
    contenedor_ancho = models.IntegerField()
    contenedor_alto = models.IntegerField()
    borde_redondeado =  models.IntegerField()
    tipo_grafico = models.CharField(max_length=50)  # ej: 'barra', 'linea', 'pastel', etc.
    var_x = models.CharField(max_length=100, blank=True, null=True)   
    var_y = models.CharField(max_length=100)
    color_relleno = models.CharField(max_length=100)
    color_texto = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contenedor_nombre} ({self.tipo_grafico}) en {self.contenedor_pestana}"
