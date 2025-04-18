from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import TablaUsuario
from .utils import datos  # 
import re
#   si no quiero retornar nada   return HttpResponse(status=204)  # 204 No Content


def main(request):
    return render(request,'main.html')

@csrf_exempt
def cargar_datos(request):
    """     conectarse al SGDB que donde el cliente almacene sus datos    """

    if  request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    # SI ES POST OBTENDRÁ LA TABLA
    try:
        data = json.loads(request.body)
        fuente= data.get("fuente")
        
        if fuente == "csv":
            ruta =  data.get("ruta")
            sep = data.get("sep")
            df = pd.read_csv(ruta,sep=sep)
        else:
            df = datos.importar_desde_db(data)

        df.columns = [re.sub(r"[ .,;:]","",col) for col in df.columns ]        

        
        nombre_tabla = data.get("nombre_tabla")
        usuario = data.get("usuario_db")
        password = data.get("password_db")
        base_datos = data.get("nombre_db")
        datos.guardar_datos_usuario(usuario, password, base_datos,nombre_tabla)

        conexion = datos.obtener_conexion_mysql()
        datos.crear_tabla(nombre_tabla, df, conexion) # crea la tabla e inserta los datos
        conexion.dispose()

        return datos.retornarJSON_tabla(df,msg="cargados y guardados",nrow=10)
    
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
        filtro = data.get("filtro")
        persistente = data.get("persistente") # boolean
        df = datos.select_df()
        df_filtrado = df.query(filtro)
        if persistente == True: 
            conexion = data.obtener_conexion_mysql()
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
        return JsonResponse({"error","Método no permitido"},status=400)
    
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
    tipo = data.get("tipo")
    variables= data.get("variables",[None,None])
    var_y = variables[0]
    var_x = variables[1] if len(variables)==2 else None
    
    if var_y == None :
        return JsonResponse({"error":"falta seleccionar variables"},status=400)
    
    print("llegan los datos",tipo, var_y,var_x)
    df = datos.select_df()


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
        elif df[var_x].dtype =='object' or df[var_y].dtype =='object':
            return JsonResponse({"error","las variables deben ser numéricas"},status=400)
        else:
            result[var_x],result[var_y] = df[var_x].round(4).tolist(), df[var_y].round(4).tolist()
    elif tipo == 'box':
        result = datos.calcular_boxplot(df[var_y])
    elif tipo == 'box_by_category':
        result = datos.calcular_datos_box2(df,var_x,var_y)
    else:
        return JsonResponse({"error":f"No se conoce el gráfico {tipo}."},status=400)
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



