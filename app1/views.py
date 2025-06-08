from django.http import JsonResponse
from django.shortcuts import render,redirect

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
import pandas as pd

import re
import os

# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserTable
from .serializers import UserTableSerializer
from .util import save_user_table


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_table_name(request):
    table_name = request.data.get('table_name')
    data, errors = save_user_table(request.user, table_name)
    if errors:
        return Response(errors, status=400)
    return Response(data, status=201)
    # table_name = request.data.get('table_name')
    # if not table_name:
    #     return Response({"table_name": "Este campo es requerido."}, status=400)
    
    # # Buscar si el usuario ya tiene alguna base de datos asignada
    # user_tables = UserTable.objects.filter(user=request.user)
    # if user_tables.exists():
    #     # Si hay registros, reutilizar el db_name del primer registro (o el que quieras)
    #     db_name = user_tables.first().db_name
    # else:
    #     # Si no hay registros, crear un nombre nuevo para la base de datos
    #     db_name = f"db_for_{request.user.username}"
    #     # Aquí podrías crear la base de datos físicamente si quieres
    
    # data = {
    #     "table_name": table_name,
    #     "db_name": db_name,
    # }
    
    # serializer = UserTableSerializer(data=data)
    # if serializer.is_valid():
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=201)
    # return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_table(request):
    ultima_tabla = UserTable.objects.filter(user=request.user).order_by('-created_at').first()
    if ultima_tabla:
        serializer = UserTableSerializer(ultima_tabla)
        return Response(serializer.data)
    return Response({"detail": "No hay tablas registradas."}, status=404)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserTable
from .serializers import UserTableSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def table_name_list(request):
    tablas = UserTable.objects.filter(user=request.user).order_by('-created_at')
    
    serializer = UserTableSerializer(tablas, many=True)
    return Response(serializer.data, status=200)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        if password1 != password2:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password1)
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class SigninView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        response = super(SigninView, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key})
    

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class VerifyTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("Verificando auth_token")
        print("Username:", request.user.username)
        print("ID:", request.user.id)
        return Response({"message": "Token válido."})
    


# BACK END WEB

def home(request):
    return render(request,'main.html')



from django.http import JsonResponse
from django.views.decorators.http import require_POST
#@require_POST


@api_view(['POST'])
def subir_csv(request):

    archivo = request.FILES.get('file_csv')
    sep = request.POST.get('sep',';')
    encoding =request.POST.get('encoding','utf-8') 
    nombre_tabla = request.POST.get('nombre_tabla_csv')

    

    if archivo and sep and nombre_tabla:
        # Procesar archivo, guardar en base de datos, etc.
        print("Archivo csv",archivo,"sep",sep,"Nombre tabla",nombre_tabla)
        df = pd.read_csv(archivo,sep=sep,encoding=encoding)
        print(df.head())

        tabla_completa = df[:60_000].to_dict(orient='records')
        preview = tabla_completa[:50] 

        data, errors = save_user_table(request.user, nombre_tabla)
        if errors:
            return Response(errors, status=400)
        return JsonResponse({
                "mensaje": "Archivo procesado con éxito",
                "tablaCompleta": tabla_completa,  # Toda la tabla (máximo 60.000)
                "preview": preview
            }, safe=False)
    else:
        return JsonResponse({"error": "Faltan campos"}, status=400)



@require_POST
def subir_excel(request):

    archivo = request.FILES.get('file')
    hoja = request.POST.get('hoja')
    nombre_tabla = request.POST.get('nombre_tabla_excel')

    

    if archivo and hoja and nombre_tabla:
        # Procesar archivo, guardar en base de datos, etc.
        print("Archivo",archivo,"hoja",hoja,"Nombre tabla",nombre_tabla)
        df = pd.read_excel(archivo,sheet_name=hoja)
        df_preview = df.head(50).to_dict(orient='records')
        print(df.head())
        
        data, errors = save_user_table(request.user, nombre_tabla)
        if errors:
            return Response(errors, status=400)
        return JsonResponse({   "mensaje": "Archivo procesado con éxito",
                                "preview": df_preview})
    else:
        return JsonResponse({"error": "Faltan campos"}, status=400)
    



import pymysql
import psycopg2
import pyodbc

@require_POST
def conectarse_sgbd_cliente(request):
    try:
        usuario = request.POST.get('usuario')
        password = request.POST.get('pass')
        host = request.POST.get('host')
        puerto = request.POST.get('puerto')
        base_datos = request.POST.get('bd')
        consulta = request.POST.get('consulta')
        nombre_tabla = request.POST.get('nombre_tabla')
        tipo_sgbd = request.POST.get('tipo_sgbd')  

        if not all([usuario, password, host, puerto, base_datos, consulta, nombre_tabla, tipo_sgbd]):
            return JsonResponse({"error": "Faltan campos"}, status=400)

        if tipo_sgbd == "MySQL":
            conn = pymysql.connect(
                host=host,
                user=usuario,
                password=password,
                port=int(puerto),
                database=base_datos
            )
        elif tipo_sgbd == "PostgreSQL":
            conn = psycopg2.connect(
                host=host,
                user=usuario,
                password=password,
                port=int(puerto),
                dbname=base_datos
            )
        elif tipo_sgbd == "Microsoft_SQL_Server":
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={host},{puerto};DATABASE={base_datos};UID={usuario};PWD={password}"
            )
            conn = pyodbc.connect(conn_str)
        else:
            return JsonResponse({"error": "SGBD no soportado"}, status=400)

        df = pd.read_sql(consulta, conn)
        print(df.head())
        conn.close()

        df_preview = df.head(50).to_dict(orient='records')
        print(df.head())
        
        data, errors = save_user_table(request.user, nombre_tabla)
        if errors:
            return Response(errors, status=400)
        return JsonResponse({  "mensaje": f"Consulta ejecutada con éxito. Filas: {df.shape[0]}, Columnas: {df.shape[1]}",
                                "preview": df_preview})


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






def signin(request):
    return render(request,'signin.html')




import pymysql
import pandas as pd

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserTable
import pymysql
import pandas as pd

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cargar_tabla_usuario(request):
    try:
        # 1. Usuario autenticado
        user = request.user

        # 2. Obtener la última tabla asociada a ese usuario
        ultima_tabla = UserTable.objects.filter(user=user).order_by('-created_at').first()
        if not ultima_tabla:
            return Response({"error": "No se encontró ninguna tabla registrada para este usuario."}, status=404)

        nombre_tabla = ultima_tabla.table_name

        # 3. Conexión a la base de datos MySQL
        conn = pymysql.connect(
            host='localhost',
            user='cliente',
            password='cliente1234',
            database='db_cliente_for_milton24',
            port=3306
        )

        # 4. Ejecutar consulta y devolver datos
        query = f"SELECT * FROM `{nombre_tabla}` "
        df = pd.read_sql(query, conn)
        conn.close()

        tabla_completa = df.to_dict(orient='records')
        preview = df.head(50).to_dict(orient='records')
        return Response({
            "mensaje": f"Datos de la tabla '{nombre_tabla}' cargados correctamente.",
            "tablaCompleta": tabla_completa,
            "preview":preview,
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)





from .models import UserTable, ContenidoRelacionado

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def guardar_contenido_multiple(request):
    print("--Guardadno contenido")
    user = request.user
    table_name = request.data.get("table_name")
    contenidos = request.data.get("contenidos")  # Este es un diccionario

    if not table_name or not contenidos:
        return Response({"error": "Faltan campos requeridos"}, status=400)

    try:
        user_table = UserTable.objects.get(user=user, table_name=table_name)
    except UserTable.DoesNotExist:
        return Response({"error": "Tabla no encontrada"}, status=404)

    mensajes = []

    for tipo, contenido_lista in contenidos.items():
        if not isinstance(contenido_lista, list):
            continue  # ignorar si no es lista

        obj, creado = ContenidoRelacionado.objects.update_or_create(
            table=user_table,
            tipo=tipo,
            defaults={"contenido": json.dumps(contenido_lista)}  # Guardamos como string
        )

        if creado:
            mensajes.append(f"✔ {tipo.capitalize()} creado.")
        else:
            mensajes.append(f"✏ {tipo.capitalize()} actualizado.")
    print("--✅ contenido guardado con éxito")
    return Response({"success": "Contenidos procesados.", "detalles": mensajes}, status=200)




from collections import defaultdict


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_contenido(request):
    print("--Obteniendo contendido")
    table_name = request.query_params.get("table_name")

    if not table_name:
        return Response({"error": "Falta el nombre de la tabla"}, status=400)

    try:
        user_table = UserTable.objects.get(user=request.user, table_name=table_name)
    except UserTable.DoesNotExist:
        return Response({"error": "Tabla no encontrada"}, status=404)

    queryset = ContenidoRelacionado.objects.filter(table=user_table).order_by("-fecha_creacion")

    # Agrupar por tipo: nota, estadistica, modelo
    agrupado = defaultdict(list)

    for item in queryset:
        try:
            contenido = json.loads(item.contenido)  # Convertir de string a lista
        except json.JSONDecodeError:
            contenido = []

        agrupado[item.tipo].extend(contenido)
    print("-- ✅ Contendio obtendio con exito")
    return Response({
        "notas": agrupado.get("nota", []),
        "estadisticas": agrupado.get("estadistica", []),
        "modelos": agrupado.get("modelo", [])
    }, status=200)





# from .models import Grafico
# from .serializers import GraficoSerializer

# class ListaGraficos(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         graficos = Grafico.objects.filter(usuario=request.user)
#         serializer = GraficoSerializer(graficos, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         data = request.data.copy()
#         data['usuario'] = request.user.id
#         serializer = GraficoSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .models import UserTable, TextBox

#@api_view(['POST'])
class GuardarTextBoxView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Datos recibidos:", request.data)
        data = request.data
        user = request.user

        table_name = data.get("table_name")
        if not table_name:
            return Response({"error": "Falta el nombre de tabla"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_table = UserTable.objects.get(user=user, table_name=table_name)
        except UserTable.DoesNotExist:
            return Response({"error": "Tabla no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        required_fields = [
            "contenedor_nombre", "contenedor_pestana", "contenedor_x", "contenedor_y",
            "contenedor_ancho", "contenedor_alto", "color_frame", "borde_redondeado",
             "textbox_contenido", "textbox_negrita",
            "textbox_tamaño_letra", "textbox_capitalizado", "textbox_underline", "textbox_fuente","textbox_color",'textbox_fondo_color' 
        ]

        for field in required_fields:
            if field not in data:
                return Response({"error": f"Falta el campo: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        textbox, created = TextBox.objects.update_or_create(
            table=user_table,
            contenedor_nombre=data["contenedor_nombre"],
            defaults={
                "contenedor_pestana": data["contenedor_pestana"],
                "contenedor_x": data["contenedor_x"],
                "contenedor_y": data["contenedor_y"],
                "contenedor_ancho": data["contenedor_ancho"],
                "contenedor_alto": data["contenedor_alto"],
                "color_frame": data["color_frame"],
                "borde_redondeado": data["borde_redondeado"],
                "textbox_contenido": data["textbox_contenido"],
                "textbox_negrita": data["textbox_negrita"],
                "textbox_tamaño_letra": data["textbox_tamaño_letra"],
                "textbox_capitalizado": data["textbox_capitalizado"],
                "textbox_underline": data["textbox_underline"],
                "textbox_fuente": data["textbox_fuente"],
                "textbox_color": data["textbox_color"],
                'textbox_fondo_color':data['textbox_fondo_color']
            }
        )
        print("-- ✅ Texbox guardado con exito")
        return Response({
            "status": "ok",
            "created": created,
            "id": textbox.id
        }, status=status.HTTP_200_OK)



class ObtenerTextBoxesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        table_name = request.query_params.get("table_name")
        if not table_name:
            return Response({"error": "Falta el nombre de tabla"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_table = UserTable.objects.get(user=user, table_name=table_name)
        except UserTable.DoesNotExist:
            return Response({"error": "Tabla no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        textboxes = TextBox.objects.filter(table=user_table)
        data = []
        for tb in textboxes:
            data.append({
                "id": tb.id,
                "contenedor_nombre": tb.contenedor_nombre,
                "contenedor_pestana": tb.contenedor_pestana,
                "contenedor_x": tb.contenedor_x,
                "contenedor_y": tb.contenedor_y,
                "contenedor_ancho": tb.contenedor_ancho,
                "contenedor_alto": tb.contenedor_alto,
                "color_frame": tb.color_frame,
                "borde_redondeado": tb.borde_redondeado,
                "textbox_contenido": tb.textbox_contenido,
                "textbox_negrita": tb.textbox_negrita,
                "textbox_tamaño_letra": tb.textbox_tamaño_letra,
                "textbox_capitalizado": tb.textbox_capitalizado,
                "textbox_underline": tb.textbox_underline,
                "textbox_fuente": tb.textbox_fuente,
                "textbox_color": tb.textbox_color,
                'textbox_fondo_color':tb.textbox_fondo_color
            })
        print("-- ✅ Texboxes obtenido con exito")
        return Response(data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_textbox(request):
    table_name = request.data.get('table_name')
    contenedor_nombre = request.data.get('contenedor_nombre')
    user = request.user  # Usuario autenticado

    if not table_name or not contenedor_nombre:
        return Response({"detail": "Faltan parámetros: table_name o contenedor_nombre"}, status=400)

    # Obtener la tabla del usuario
    try:
        user_table = user.tables.get(table_name=table_name)
    except UserTable.DoesNotExist:
        return Response({"detail": "No existe la tabla especificada"}, status=404)

    # Buscar el TextBox por contenedor_nombre y la tabla
    try:
        textbox = TextBox.objects.get(table=user_table, contenedor_nombre=contenedor_nombre)
    except TextBox.DoesNotExist:
        return Response({"detail": "No se encontró el TextBox especificado"}, status=404)

    # Eliminar el TextBox
    textbox.delete()

    return Response({"detail": "TextBox eliminado correctamente"}, status=204)

