from rest_framework import serializers
from .models import UserTable

class UserTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTable
        fields = ['table_name', 'db_name','created_at']  # no incluimos el usuario porque lo tomamos del request



# from .models import Grafico

# class GraficoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Grafico
#         fields = '__all__'