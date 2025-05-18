from django.shortcuts import get_object_or_404
from django.db import connection

from sqlalchemy import create_engine,text
from pandas import read_sql
import numpy as np
import pandas as pd
from pandas import DataFrame, read_json
from django.http import JsonResponse
import plotly.express as px


from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage
import json
from sklearn.model_selection import train_test_split


from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import  confusion_matrix, classification_report,roc_curve, auc, r2_score,mean_squared_error
from sklearn.model_selection import GridSearchCV,RandomizedSearchCV

from app1.models import UserTable
import mysql.connector
import re

VAR_CONEXION_CLIENTE = {}
VAR_CONEXION_SERVIDOR = {
    "USER": "cliente",
    "PASSWORD": "cliente1234",
    "HOST": "localhost",
    "PUERTO": 3306,
    "DB": "db_clientes",
    "URL":  f"mysql+mysqlconnector://cliente:cliente1234@localhost/",
  
}






sgbd = {
    "MySQL": lambda user, password, db, host, port: f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}",
    "PostgreSQL": lambda user, password, db, host, port: f"postgresql://{user}:{password}@{host}:{port}/{db}",
    "SQLServer": lambda user, password, db, host, port: f"mssql+pyodbc://{user}:{password}@{host},{port}/{db}?driver=ODBC+Driver+17+for+SQL+Server",
}


transformadores = {
    'ln': np.log,
    'log10':np.log10,
    'sqrt':np.sqrt,
    'exp': np.exp,
    'square':np.square,
    'abs':np.abs,
}

estadisticos = {
    "media": np.mean,
    "mediana": np.median,
    "desviacion_estandar": np.std,
    "varianza": np.var,
    "minimo": np.min,
    "maximo": np.max
}


modelos_dic = {
    # Regresores
    "linear_regression": LinearRegression(),
    "random_forest_regressor": RandomForestRegressor(),
    "decision_tree_regressor": DecisionTreeRegressor(),
    "svm_regressor": SVR(),
    "knn_regressor": KNeighborsRegressor(),
    
    # Clasificadores
    "logistic_regression": LogisticRegression(),
    "random_forest_classifier": RandomForestClassifier(),
    "decision_tree_classifier": DecisionTreeClassifier(),
    "svm_classifier": SVC(probability=True),
    "knn_classifier": KNeighborsClassifier(),
    "naive_bayes": GaussianNB(),
}

tipo_grafico_dic = {
    'scatter': px.scatter,
    'line': px.line,
    'area': px.area,
    'box': px.box,
    'bar':px.bar,
    'pie':px.pie,
}




def importar_desde_db(data):
    SGBD = data.get("SGBD")
    usuario= data.get("usuario_db")
    password = data.get("password_db")
    base_de_datos =data.get("db")
    host = data.get("host")
    puerto  =data.get("puerto")
    consulta = data.get("consulta")
    print("---parametros de conexion:")
    print(usuario,password,base_de_datos,host,consulta,puerto)
    try:
        str_engine = sgbd[SGBD](usuario, password, base_de_datos,host,puerto)
        print(str_engine)
        engine = create_engine(str_engine)
        return read_sql(consulta,engine)
    except Exception as e:
        print({"error": f"Error de conexión a la base de datos: {str(e)}"})
        return DataFrame()
    finally:
        if engine is not None:
            engine.dispose()



def crear_db_clientes(nombre_tabla, df, user):
    pass


def obtener_conexion_mysql():
    try:
        print("++ Obteniendo conexión con MySQL para almacenar datos en nuestro servidor")
        url = VAR_CONEXION_SERVIDOR["URL"]
        engine = create_engine(url)
        print("Variable de conexión con MySQL (servidor)")
        print(url)

        # Testear la conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as err:
        raise ValueError(f"Error al conectar con MySQL: {err}")



def crear_tabla( df, engine):
    nombre_tabla = VAR_CONEXION_CLIENTE["NOMBRE_TABLA"]
    print(df.head())
    try:
        df.to_sql(nombre_tabla, con=engine, if_exists='replace', index=False)
    except Exception as ex:
        raise ValueError(f"Error al crear la tabla: {str(ex)}")


        
def actualizar_dataframe(df, engine, modo="replace"):
    """
    Actualiza los datos en una tabla MySQL usando SQLAlchemy.

    Parámetros:
    - df: DataFrame con los datos
    - nombre_tabla: nombre de la tabla
    - engine: conexión SQLAlchemy
    - modo: 'append' para añadir, 'replace' para eliminar e insertar, 'fail' para lanzar error si ya existe
    """
    if modo not in ["append", "replace", "fail"]:
        raise ValueError(f"Modo '{modo}' no válido. Usa 'append', 'replace' o 'fail'.")

    nombre_tabla = VAR_CONEXION_CLIENTE["NOMBRE_TABLA"]
    try:
        df.to_sql(nombre_tabla, con=engine, if_exists=modo, index=False)
    except Exception as ex:
        raise ValueError(f"Error al insertar datos: {str(ex)}")


def select_df():
    try:
        nombre_tabla =  ""
        url = ""
        engine = create_engine(url)
        df = read_sql(f"SELECT * FROM {nombre_tabla}",engine)
        return df
    
    except Exception as ex:
                print({"error": f"Error al consultar la tabla del usuario a la base de datos: {str(ex)}"})
    finally:
        if engine is not None:
            engine.dispose()


def retornarJSON_tabla(df,msg,nrow=10):
    return JsonResponse({
                "mensaje": f" Datos {msg} correctamente.",
                "columnas":list(df.columns),
                "filas":df.head(nrow).to_dict(orient="records"),
                })


def transformar_cols(data):
    columnas = data.get("columnas")
    op = data.get("op")
    df = select_df()
    func = transformadores[op]
    array = func(df[columnas])
    new_cols = [f"{op}_{col}" for col in columnas]
    new_cols = new_cols[0] if len(new_cols)==1 else new_cols
    df[new_cols] = array
    conexion = obtener_conexion_mysql()
    crear_tabla(df,conexion)
    conexion.dispose()
    return df

def aplicar_ans(data):
    df = select_df()
    columnas = data.get(columnas)
    op = data.get(op)
    

    if op == "PCA":
        scaler= StandardScaler()
        scaledX = scaler.fit_transform(df[columnas])
        n_componentes = data.get(n_componentes)
        pca= PCA(n_components=n_componentes,random_state=42)
        X_pca = pca.fit_transform(scaledX)
        df = pd.DataFrame(X_pca,columns=[ f"comp{i+1}" for i in range(X_pca.shape[1])])

    elif op == "Kmeans":
        n_clusters = data.get(n_clusters)
        kmeans = KMeans(n_clusters=n_clusters,random_state=42)
        kmeans_labels = kmeans.fit_predict(scaledX).reshape(-1,1)
        df["cluster"] = kmeans_labels
        
    elif op == "linkage":
        linked = linkage(scaledX, method='ward')
        clusters =  pd.DataFrame(linked,columns=[f"clt{i+1}" for i in range(linked.shape[1])])
        df[clusters.columns] = clusters.values
    
    conexion = obtener_conexion_mysql()
    crear_tabla(df,conexion)
    conexion.dispose()
    return df


def obtener_dict_estadisticos(data):
    """             son funcioens resumenes             """
    print("LLego al back-end")
    try:
        
        columnas = data.get("variables")
        func =estadisticos[ data.get("tipo")]
        df = select_df()
        array_resumen = func(df[columnas])
        return array_resumen.round(4).to_dict(),200
    except json.JSONDecodeError as e:
        return {"error": f"Error en los datos: {str(e)}"},400
    


"""   recibe un json con modelos: [lista de modelos], tipo: regr o cls  , var_dep: y , test_size, """
def realizar_entrenamiento(data):
    try:
        modelo_elegido = data.get("modelo")  # Nombre de los modelos
        tipo_modelo = data.get("tipo")
        busqueda = data.get("busqueda") # Boolean
        df = select_df()

        print(df.head())
        X = df.iloc[:,1:]
        y = df.iloc[:,0] 

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # PREGUNTA SI EXISTE BUSQUEDA    
        if  busqueda == True :
            result_search,codigo =  realizar_busqueda(X_train,y_train,X_test,y_test,data)
            return result_search,codigo
        
        # metricas sin ajustar hiperparametros        
        if modelo_elegido in modelos_dic:          
            modelo = modelos_dic[modelo_elegido]
            modelo.fit(X_train, y_train)
            result_metrica,codigo = calcular_metricas(modelo,X_test,y_test,tipo_modelo)
            return result_metrica,codigo
        
        return {"error": "La opción elegida no es válida"},400
        
    except json.JSONDecodeError as ex:
        return {"error": f"Error en los datos: {str(ex)}"},400
        
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"},500
    

def calcular_metricas(modelo,X_test,y_test,tipo_modelo):
    y_pred = modelo.predict(X_test)
    print("calculadon metrica.............................................")

    if tipo_modelo == "regresion":
        mse = round(mean_squared_error(y_test, y_pred),4)
        rmse = round(np.sqrt(mse),4)
        r2 = round(r2_score(y_test, y_pred),4)
        return {"mse":mse,"rmse":rmse,"R^2": r2},200
    elif tipo_modelo == "clasificacion":
        y_scores = modelo.predict_proba(X_test)[:,1]
        report = classification_report(y_true= y_test,y_pred=y_pred)
        print(report)
        matriz_confusion = confusion_matrix(y_true=y_test,y_pred=y_pred).tolist()
        print(matriz_confusion)
        fpr,tpr,_ = roc_curve(y_test,y_scores)
        auc_score = round(auc(fpr,tpr),4)
        return {"report":report,"matriz_confusion":matriz_confusion,"auc_score": auc_score},200
    else:
        return {"error":"No se ha encontrado el modelo elegido"},400

def realizar_busqueda(X_train,y_train,X_test,y_test,data):

    modelo_elegido = data.get("modelo")  # Nombre de los modelos
    hiperparametros = data.get("params")
    scoring = data.get("scoring")
    tipo_busqueda = data.get("tipo_busqueda")
    cv = data.get("cv")

    if tipo_busqueda == "GridSearchCV" and modelo_elegido in modelos_dic :
        modelo = modelos_dic[modelo_elegido]
        search = GridSearchCV(
            modelo,
            hiperparametros,
            cv=cv,
            scoring=scoring,
            n_jobs=-1
        )
        search.fit(X_train,y_train)
        result_search = {"best_estamador": search.best_estimator_, 
                        "best_params": search.best_params_,
                        "best_score": search.best_score_}
        best_estimator = search.best_estimator_
        y_pred = best_estimator.predict(X_test)
        mse,rmse = mean_squared_error(y_test,y_pred), np.sqrt(mse)
        metricas = {"mse": mse, "rmse":rmse}
        return {"search":result_search,"metricas":metricas},200
    elif tipo_busqueda =="RandomizedSearchCV" and modelo_elegido in modelos_dic:
        n_iter = data.get("n_iter")
        modelo = modelos_dic[modelo_elegido]
        search = RandomizedSearchCV(
            modelo,
            hiperparametros,
            cv=cv,
            scoring=scoring,
            n_iter=n_iter,
            n_jobs=-1
        )
        search.fit(X_train,y_train)
        result_search ={"best_estamador": search.best_estimator_, 
                                        "best_params": search.best_params_,
                                        "best_score": search.best_score_}
        best_estimator = search.best_estimator_
        y_pred = best_estimator.predict(X_test)
        mse,rmse = mean_squared_error(y_test,y_pred), np.sqrt(mse)
        metricas = {"mse": mse, "rmse":rmse}
        return {"search":result_search,"metricas":metricas},200
    else:
        return {"error": "La opción elegida no es válida"},400






# Función para calcular los valores del box plot
def calcular_boxplot(grupo):
    q1,median,q3 = [ np.round(np.percentile(grupo, per),4) for per in range(25,76,25) ]  # cuartiles
    min_val,max_val = np.round(grupo.min(),4), np.round(grupo.max(),4)  #min y  Máximo
    iqr = q3 - q1  # Rango intercuartílico
    lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr # limites
    outliers = grupo[(grupo < lower_bound) | (grupo > upper_bound)].round(4).tolist()  # Detectar outliers
    return {'min': float(min_val), 'q1': float(q1), 'median': float(median), 'q3': float(q3), 'max': float(max_val), 'outliers': outliers}

# Aplicar la función a cada categoría

def calcular_datos_box2(df,var_x,var_y):   
    dict_por_categoria = df.groupby(var_x)[var_y].apply(calcular_boxplot).to_dict()
    cat = {}
    valores = {}
    for key,values in dict_por_categoria.items():
        valores[key[1]] = values
        if key[1]== 'outliers':
            cat[key[0]] = valores
            valores = {}
    # Mostrar resultado
    print(cat)
    return cat
























