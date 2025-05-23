from django.http import JsonResponse
from django.shortcuts import render,redirect

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
import pandas as pd
from .utils import datos  # 
from .forms import TaskForm
import re
import os

#   si no quiero retornar nada   return HttpResponse(status=204)  # 204 No Content

def home(request):
    return render(request,'home.html')

def create_task(request):
    if request.method == 'GET':
        return render(request,'create_task.html',{
            'form': TaskForm(),
        })
    else:
        try:
            print("--- Datos del Formulario de la Tarea")
            print(request.POST)
            form =TaskForm(request.POST) # form en html rellenado
            new_task = form.save(commit=False) # no guarda en bbdd y retorna el form
            new_task.user = request.user
            new_task.save()# 
            print(new_task)
            return render(request,'create_task.html',{
                'form': TaskForm(),
            })
        except ValueError:
            return render(request,'create_task.html',{
            'form': TaskForm(),
            'error': "Error al crear la tarea"
            }) 
    
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request,'signin.html',{
            'form': AuthenticationForm,
        })
    
    elif request.method == 'POST':
        print("Inicio de sesióon")
        print(request.POST)
        user = authenticate(request,
                      username=request.POST.get("username"),
                      password=request.POST.get("password")
                      )
        if user is None:
            return render(request,'signin.html',{
                'form':AuthenticationForm,
                'error':'El usuario o la contraseña no existen'
            })
        else:
            login(request,user) #cookies
            return redirect('main')
    

def signup(request):

    # Cliente entra en la página
    if request.method == 'GET':
        print("El cliente a visitado la página")
        print('Datos del GET:')
        print(request.GET)
        
        return render(request,'signup.html',{
            'form':UserCreationForm,
        })


    if request.method == 'POST':
        print('El cliente ha enviado el formulario')
        print('Datos del POST:')
        print(request.POST)

        if request.POST['password1'] != request.POST['password2']:
            return render(request,'signup.html',{
                'form': UserCreationForm,
                'error': 'Las contraseñas no coinciden'
                })
        
        else:
            print("las contraseañas coinciden")
            try:
                user = User.objects.create_user(
                        username=request.POST.get("username"),
                        password=request.POST.get("password1")
                    )
                user.save()
                login(request,user)
                return redirect(to='main')
            except IntegrityError:
                return render(request,'signup.html',{
                    'form': UserCreationForm,
                    'error': "El usuario ya existe"
                })
            
        
def main(request):
    return render(request,'main.html')


# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserTable
from .serializers import UserTableSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_table_name(request):
    table_name = request.data.get('table_name')
    if not table_name:
        return Response({"table_name": "Este campo es requerido."}, status=400)
    
    # Buscar si el usuario ya tiene alguna base de datos asignada
    user_tables = UserTable.objects.filter(user=request.user)
    if user_tables.exists():
        # Si hay registros, reutilizar el db_name del primer registro (o el que quieras)
        db_name = user_tables.first().db_name
    else:
        # Si no hay registros, crear un nombre nuevo para la base de datos
        db_name = f"db_for_{request.user.username}"
        # Aquí podrías crear la base de datos físicamente si quieres
    
    data = {
        "table_name": table_name,
        "db_name": db_name,
    }
    
    serializer = UserTableSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


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

@csrf_exempt
def cargar_datos(request):

    print("--- Función View: /cargar_datos")
    if  request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    
    
    try:


        content_type = request.content_type

        if content_type == "application/json":
            data = json.loads(request.body)
            fuente = data.get("fuente")

        else:
            data = request.POST
            fuente = data.get("fuente")
        if fuente == "csv":

            print("--- Recibiendo: Archivo CSV (binario)")
            file =  request.FILES.get("file")
            sep = request.POST.get("sep")
            df = pd.read_csv(file,sep=sep)
            nombre_tabla = os.path.splitext(os.path.basename(file.name))[0]
            print("nombre tabla",nombre_tabla)
        elif fuente == "excel":

            print("--- Recibiendo: Archivo Excel (binario)")
            file = request.FILES.get("file")
            sheet_name= request.POST.get("sheet_name")
            df = pd.read_excel(file,sheet_name=sheet_name)
            nombre_tabla = os.path.splitext(os.path.basename(file.name))[0]
            print("---nombre tabla:",nombre_tabla)

        elif fuente == "SGBD":

            print("--- Recibienddo: credenciales para conectarse a SGBD")
            data = json.loads(request.body)
            df = datos.importar_desde_db(data)

            nombre_tabla = data.get("nombre_tabla")
            print("nombre tabla",nombre_tabla)
            print("---✅ Ver Info")
            df.info()
            print("--- BBDD Ha lleado al BackEnd", "\n--- Limpiando Columnas con carácteres Raros")
            df.columns = [re.sub(r"[ .,;:]","",col) for col in df.columns ]        
            
            print("--- Guardando BBDD en nuestro Servidor")
            # datos.crear_db_clientes(nombre_tabla=nombre_tabla,df = df,user=request.user)

            print("--- ✅ Guardado Correctamente")

            print("--- saliendo de vista cargar_datos()")

            
            df_subset = df.head(50).to_dict(orient="records")
            return JsonResponse(
                data=df_subset,
                safe=False
            )
        else:
            print("--- ❌ La fuente de datos No es la correcta")
            raise Exception("La Fuente de BBDD seleccionada no es Valida. ")

        print("---✅ Ver Info")
        df.info()
        
        print("--- BBDD Ha lleado al BackEnd", "\n--- Limpiando Columnas con carácteres Raros")
        df.columns = [re.sub(r"[ .,;:]","",col) for col in df.columns ]        
        
        print("--- Guardando BBDD en nuestro Servidor")
        # datos.crear_db_clientes(nombre_tabla=nombre_tabla,df = df,user=request.user)

        print("--- ✅ Guardado Correctamente")
        print("--- saliendo de vista cargar_datos()")
        return JsonResponse({
                    "mensaje": f" Datos correctamente guardados en bbdd."
                    })
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)
    except ValueError as ex:
        return JsonResponse({"error": str(ex)}, status=400)
    except Exception as ex:
        return JsonResponse({"error": f"Error inesperado: {str(ex)}"}, status=500)
    

@csrf_exempt
def filtrar(request):
    """          filtra filas segun el valor propocinado por el campo filtrar               """
    if request.method != "POST":
        return JsonResponse({"error","Método no permitido"},status=400)
    
    # SI ES POST filtrará LA TABLA
    try:
        data = json.loads(request.body)
        print(data)
        filtro = data.get("filtro")
        df = datos.select_df()
        try:
            df_filtrado = df.query(filtro)
        except pd.errors.QuerySyntaxError as e:
            return JsonResponse({"error": "Error en la sintaxis del filtro"}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Columna no encontrada: {str(e)}"}, status=400)
        

        conexion = datos.obtener_conexion_mysql()
        datos.actualizar_dataframe(df,conexion)
        conexion.dispose()
        return datos.retornarJSON_tabla(df_filtrado,msg="filtrados")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def elegir_columnas(request):
    if request.method != "POST":
        return JsonResponse({"error":"Método no permitido"},status=400)
    
    # recibe un json con {"columnas": [col1,col2,etc]}
    try:
        data = json.loads(request.body)
        columnas = data.get("columnas",None)
        df = datos.select_df()
        if columnas: 
            df = df[columnas]
            conexion = datos.obtener_conexion_mysql()
            datos.actualizar_dataframe(df,conexion)
            conexion.dispose()      # actualiza dataframe de session
        return datos.retornarJSON_tabla(df,msg="eliminados")
    
    except json.JSONDecodeError:
          return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def transformar_variables(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)
    
    """ recibe un json con el nombre la columna y el tipo de operacion del combo box """
    try:
        data = json.loads(request.body)
 
        if data.get("tipo") == "ANS": df = datos.aplicar_ans(data)
        else: df = datos.transformar_cols(data)

        return datos.retornarJSON_tabla(df,"transformados")
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"},status=400)    
    except Exception as e:
        return JsonResponse({"error":str(e)},status=500)
    

# check
@csrf_exempt
def obtener_datos_grafico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)

    data = json.loads(request.body)
    tipo = data.get("tipo") # categorico , numerico , continuo
    

    df = datos.select_df()


    result = {}
    if tipo == 'categorico':  # bar, pie
        variable_categorica = data.get("variable_categorica")
        freq = df[variable_categorica].value_counts(normalize=False,sort=True,ascending=True)
        label = freq.index.tolist()
        valores = freq.values.round(4).tolist()
        result["label"],result["valores"] = label,valores

    # ['line','scatter','area']
    elif tipo == "numerico": 
       var_x,var_y = data.get("variables_numericas")
       df.sort_values([var_x],ascending=True,inplace=True)
       result["var_x"],result["var_y"] = df[var_x].values.tolist(),df[var_y].values.tolist()
    
    elif tipo == "continuo":
        var_continua = data.get("variable_continua")
        result["valores"] = df[var_continua].values.tolist()
    
    elif tipo == "continuo_categorico":
        var_continua, var_categorica = data.get("variables")
        agrupado = df.groupby(var_categorica)[var_continua].apply(list).to_dict()
        result = agrupado
    else:
        JsonResponse({"error":f"No se reconoce {tipo} como un tipo de variable/s reconocible"})
    
    return JsonResponse(result) 


@csrf_exempt
def generar_estadistico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)
    data = json.loads(request.body)
    resultado,status = datos.obtener_dict_estadisticos(data)
    
    return JsonResponse(resultado,status=status)


@csrf_exempt
def entrenar_modelo(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=400)
    
    data = json.loads(request.body)
    resumen,status = datos.realizar_entrenamiento(data)
    return JsonResponse(resumen,status=status)

@csrf_exempt
def get_columns_name(request):
    df = datos.select_df()
    columns = list(df.columns)
    
    return JsonResponse({
        "columnas": columns
    })



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
