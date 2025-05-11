from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=100)
    db = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.title 
    
from django.contrib.auth.models import User

class BaseDeDatosUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    db_name = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)