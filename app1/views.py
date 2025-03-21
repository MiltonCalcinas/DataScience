from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import TablaUsuario
from .utils.datos  import cargar_desde_db, retornarJSON_tabla, transformar_cols,aplicar_ans,obtener_dict_estadisticos,realizar_entrenamiento,cargar_datos,guardar_datos_usuario,obtener_df,tipo_de_gráfico
# Create your views here.
#   si no quiero retornar nada   return HttpResponse(status=204)  # 204 No Content


def main(request):
    return render(request,'main.html')


@csrf_exempt
def cargar_datos(request):
    if  request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    # SI ES POST OBTENDRÁ LA TABLA
    try:
        data = json.loads(request.body)
        fuente= data.get("fuente")
        if fuente == "csv":
            ruta =  request.POST.get("ruta")
            df = pd.read_csv(ruta,sep=",")
        else:
            df = cargar_desde_db(data)
        # probleema en la conexion
        if len(df) == 0:
            return JsonResponse({"error": "Problema en la conexion"}, status=500)
        # guardar en mi base de mysql      
        guardar_datos_usuario(request,data.get("nombre_tabla"))
        cargar_datos(df,request)
        return retornarJSON_tabla(df,msg="cargados y guardados",nrow=10)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)

    




@csrf_exempt
def filtrar(request):
    if request.method != "POST":
        return JsonResponse({"error","Método no permitido"},status=400)
    
    # SI ES POST filtrará LA TABLA
    try:
        filtro = json.loads(request.body).get("filtro")
        df = obtener_df(request)
        df_filtrado = df.query(filtro)
        return retornarJSON_tabla(df_filtrado,msg="filtrados")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def elegir_columnas(request):
    if request.method != "POST":
        return JsonResponse({"error","Método no permitido"},status=400)
    
    # recibe un json con {"columnas": [col1,col2,etc]}
    try:
        data = json.loads(request.body)
        columnas = data.get("columnas",[])
        df = obtener_df(request)
        if not columnas: # si no está vacio
            df = df[columnas]
            cargar_datos(df,request)        # actualiza dataframe de session
        return retornarJSON_tabla(df,msg="eliminados")
    except json.JSONDecodeError:
          return JsonResponse({"error": "Error al procesar los datos JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def elegir_filas(request):
    if request.method != "POST":
        return JsonResponse({"error","Método no permitido"},status=400)

    try:
        filtro = json.loads(request.body).get("filtro")
        df = obtener_df(request)
        df = df.query(filtro)
        cargar_datos(df,request)       # actualiza dataframe de session
        return retornarJSON_tabla(df,msg="eliminados")
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
        columnas = data.get("columnas")
        df = obtener_df(request)
        
        if data.get("tipo") == "ANS":
            n = data.get("n_components")
            cols= aplicar_ans(df,columnas,operacion,n)
            df.drop(columns=columnas,inplace=True)
            df = df.concat([df,cols],axis=1)
        else:   
            operacion =  data.get("operacion")
            df[columnas] = transformar_cols(df,columnas,operacion)
        """actualizo la tabla"""
        cargar_datos(df,request)        # actualiza dataframe de session
        return retornarJSON_tabla(df,"transformados")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error al procesar los datos JSON"},status=400)    
    except Exception as e:
        return JsonResponse({"error":str(e)},status=500)
    


def generar_grafico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)
    tipo = json.loads(request.body).get("tipo")
    var_x,var_y = json.loads(request.body).get("variables")
    df = obtener_df(request)

    # gráfico en HTML
    graph_html = tipo_de_gráfico(df,tipo,var_x,var_y)

    return JsonResponse({'grafico': graph_html})

def generar_estadistico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)
    
    resultado,status = obtener_dict_estadisticos(request)
    
    return JsonResponse(resultado,status=status)


def entrenar_modelo(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=400)
    
    resumen,status = realizar_entrenamiento(request)
    return JsonResponse(resumen,status=status)


def get_columns_name(request):
    df = obtener_df(request=request)
    columns = list(df.columns)
    return JsonResponse({
        "columnas": columns
    })


def configuarar_grafico(request):
    """ recibo un json con nombre X , y , tipo de grafico  """

    if request.method != 'POST' :
        return JsonResponse({"error":"Método no permitido"},status=400)
    
    df = obtener_df(request)
    data = json.loads(request.body)
    tipo = data.get("tipo")
    var_x,var_y = data.get("variables") # sin no tiene y recibe sin_y

