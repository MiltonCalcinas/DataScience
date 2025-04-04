from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import TablaUsuario
from .utils.datos  import cargar_desde_db, retornarJSON_tabla, transformar_cols,aplicar_ans,obtener_dict_estadisticos,realizar_entrenamiento,cargar_datos,guardar_datos_usuario,obtener_df,calcular_boxplot,calcular_datos_box2

#   si no quiero retornar nada   return HttpResponse(status=204)  # 204 No Content


def main(request):
    return render(request,'grafico_info.html')


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
    

# check
@csrf_exempt
def obtener_datos_grafico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)

    data = json.loads(request.body)
    tipo = data.get("tipo")
    var_y,var_x = data.get("variables",[None,None])
    if var_y == None :
        return JsonResponse({"error":"falta seleccionar variables"},status=400)
    
    print("llegan los datos",tipo, var_y,var_x)
    #df = obtener_df(request)
    shape= 1000
    df = pd.DataFrame(data = {
    'Valores': np.random.normal(0,20,shape),
    'Categoria': np.random.choice(np.array(['A','B','C']),shape,True,[.6,.3,.1]),
    })
    result = {}
    if tipo == 'bar':  # x es la categorica
        if var_x == None:
            return JsonResponse({"error":"Falta seleccionar las categorias "},status=400)
        df_group =  df.groupby([var_x])[var_y].sum()
        result[var_x],result[var_y] = df_group.index.tolist(), df_group.values.round(4).tolist()
    elif tipo == 'pie':
        if df[var_y].dtype == 'float':
            return JsonResponse({"error": "Debe ser categoriaca"},status=400)
        df_group = df[var_y].value_counts(True)
        result['labels'],result[var_y] = df_group.index.tolist(), df_group.values.tolist()
    elif tipo in ['line','scatter','area']: 
        if var_x == None :
            return JsonResponse({"error":"Falta seleccionar una variable para x "},status=400)
        result[var_x],result[var_y] = df[var_x].round(4).tolist(), df[var_y].round(4).tolist()
    elif tipo == 'box':
        result = calcular_boxplot(df[var_y])
    elif tipo == 'box_by_category':
        result = calcular_datos_box2(df,var_x,var_y)
    else:
        return JsonResponse({"error":f"No se conoce el gráfico {tipo}."},status=400)
    return JsonResponse(result) 


@csrf_exempt
def generar_estadistico(request):
    if request.method !='POST':
        return JsonResponse({"error":"Método no pemitido"},status=400)
    
    resultado,status = obtener_dict_estadisticos(request)
    
    return JsonResponse(resultado,status=status)


@csrf_exempt
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



