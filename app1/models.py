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
    


from django.db import models
from django.contrib.auth.models import User

class UserTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tables")
    table_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    db_name = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.user.username} - {self.table_name}"
