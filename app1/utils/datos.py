from django.shortcuts import get_object_or_404
from sqlalchemy import create_engine
from pandas import read_sql
import numpy as np
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

from app1.models import TablaUsuario 



sgbd = {
    "MySQL": lambda user, password, db, host: f"mysql+pymysql://{user}:{password}@{host}/{db}",
    "PostgreSQL": lambda user, password, db, host: f"postgresql://{user}:{password}@{host}/{db}",
    "Microsoft_SQL_Server": lambda user, password, db, host: f"mssql+pyodbc://{user}:{password}@{host}/{db}?driver=ODBC+Driver+17+for+SQL+Server",
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
    "logistic_regression": LogisticRegression(penalty="none",solver="lbfgs"),
    "random_forest_classifier": RandomForestClassifier(),
    "decision_tree_classifier": DecisionTreeClassifier(),
    "svm_classifier": SVC(probability=True),
    "knn_classifier": KNeighborsClassifier(),
    "naive_bayes": GaussianNB(),
}






def cargar_desde_db(data):
    fuente = data.get("fuente")
    nombre_tabla = data.get("nombre_tabla")
    usuario= data.get("usuario")
    password = data.get("password")
    base_de_datos =data.get("db")
    host = data.get("host")
    try:
        str_engine = sgbd[fuente](usuario, password, base_de_datos,host)
        print(str_engine)
        engine = create_engine(str_engine)
        return read_sql(f"SELECT * FROM {nombre_tabla}",engine)
    except Exception as e:
        print({"error": f"Error de conexión a la base de datos: {str(e)}"})
        return DataFrame()
    finally:
        if engine is not None:
            engine.dispose()


def guardar_datos_usuario(request,nombre_tabla):
    tabla, _ = TablaUsuario.objects.update_or_create(
        usuario=request.user.username,
        defaults={"nombre_tabla": nombre_tabla}
    )


def cargar_datos(df,request):
    try:
        nombre_tabla =  get_object_or_404(TablaUsuario, usuario=request.user.username).nombre_tabla
        engine = create_engine("mysql+pymysql://root:root@localhost/bd_dataframes")
        df.to_sql(name=nombre_tabla,con=engine,if_exists='replace',index=False)
        print(f"Los datos se han cargado en la tabla '{nombre_tabla}' de la base de datos.")
    except Exception as e:
        print({"error": f"Error al guardar la tabla del usuario a la base de datos: {str(e)}"})
    finally:
        if engine is not None:
            engine.dispose()

def obtener_df(request):
    try:
        nombre_tabla =  get_object_or_404(TablaUsuario, usuario=request.user.username).nombre_tabla
        engine = create_engine("mysql+pymysql://root:root@localhost/bd_dataframes")
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


def transformar_cols(df,columnas,op):
    transformador = transformadores[op]
    return df[columnas].apply(transformador)

def aplicar_ans(df,columnas,op,n):
    if op == "PCA":
        scaler= StandardScaler()
        scaledX = scaler.fit_transform(df[columnas])
        
        pca= PCA(n_components=n,random_state=42)
        X_pca = pca.fit_transform(scaledX)
        return DataFrame(X_pca,columns=[ f"comp{i+1}" for i in range(X_pca.shape[1])])
    elif op == "Kmeans":
        kmeans = KMeans(n_clusters=n,random_state=42)
        kmeans_labels = kmeans.fit_predict(scaledX).reshape(-1,1)
        return DataFrame(kmeans_labels,columns=["cluster"])
    else:
        linked = linkage(scaledX, method='ward')
        return DataFrame(linked,columns=[f"clt{i+1}" for i in range(linked.shape[1])])
    
def obtener_dict_estadisticos(request):
    print("LLego al back-end")
    try:
        data = json.loads(request.body)
        columnas = data.get("variables")
        estadistico =estadisticos[ data.get("tipo")]
        #df = obtener_df(request)
        shape= 1000
        df = DataFrame(data = {
            'Valores': np.random.normal(0,20,shape),
            'Categoria': np.random.choice(np.array(['A','B','C']),shape,True,[.6,.3,.1]),
        })
        return df[columnas].apply(estadistico).round(4).to_dict(),200
    except json.JSONDecodeError as e:
        return {"error": f"Error en los datos: {str(e)}"},400
    






"""   recibe un json con modelos: [lista de modelos], tipo: regr o cls  , var_dep: y , test_size, """
def realizar_entrenamiento(request):
    try:
        data = json.loads(request.body)
        modelo_elegido = data.get("modelo")  # Nombre de los modelos
        tipo_modelo = data.get("tipo")
        
        # Recuperar el DataFrame de la sesión
        df = obtener_df(request) 
        X = df.iloc[:,1:]
        y = df.iloc[:,0] 

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # realizar busqueda  de los mejor hiperparamtros         
        if  data.get("busqueda",None) :
            result_search,codigo =  busqueda(X_train,y_train,X_test,y_test,data)
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
    y_scores = modelo.predict_proba(X_test)[:,1]

    if tipo_modelo == "regresion":
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        return {"mse":mse,"rmse":rmse,"R^2": r2},200
    elif tipo_modelo == "clasificacion":
        report = classification_report(y_true= y_test,y_pred=y_pred)
        matriz_confusion = confusion_matrix(y_true=y_test,y_pred=y_pred)
        fpr,tpr,_ = roc_curve(y_test,y_scores)
        auc_score = auc(fpr,tpr)
        return {"report":report,"matriz_confusion":matriz_confusion,"auc_score": auc_score},200
    else:
        return {"error":"No se ha encontrado el modelo elegido"},400

def busqueda(X_train,y_train,X_test,y_test,data):

    modelo_elegido = data.get("modelo")  # Nombre de los modelos
    hiperparametros = data.get("params")
    scoring = data.get("scoring")
    tipo_busqueda = data.get("busqueda")
    n_iter = data.get("n_iter",5)

    if tipo_busqueda == "GridSearchCV" and modelo_elegido in modelos_dic :
        modelo = modelos_dic[modelo_elegido]
        search = GridSearchCV(
            modelo,
            hiperparametros,
            cv=5,
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
    elif busqueda=="RandomizedSearchCV" and modelo_elegido in modelos_dic:
        modelo = modelos_dic[modelo_elegido]
        search = RandomizedSearchCV(
            modelo,
            hiperparametros,
            cv=5,
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




tipo_grafico_dic = {
    'scatter': px.scatter,
    'line': px.line,
    'area': px.area,
    'box': px.box,
    'bar':px.bar,
    'pie':px.pie,
}


def tipo_de_gráfico(df,tipo_gf,tipo_var,var_x,var_y):

    if var_y != 'sin_y'  and tipo_var == 'numerico':
        fig = tipo_grafico_dic[tipo_gf](df,var_x,var_y,title=f'Gráfico de {var_y}')
    if var_y !='sin_y' and tipo_var == 'categorico':
        data_grouped = df.groupby(var_x)[var_y].sum().reset_index()
        fig = tipo_grafico_dic[tipo_gf](data_grouped,var_x,var_y,title=f'Gráfico de {var_y}')

    
    fig.update_layout(width=600) 
    return fig.to_html(full_html=False)


# Función para calcular los valores del box plot
def calcular_boxplot(grupo):
    q1,median,q3 =[ np.round(np.percentile(grupo, per),4) for per in range(25,76,25) ]  # cuartiles
    min_val,max_val = np.round(grupo.min(),4), np.round(grupo.max(),4)  #min y  Máximo
    iqr = q3 - q1  # Rango intercuartílico
    lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr # limites
    outliers = grupo[(grupo < lower_bound) | (grupo > upper_bound)].round(4).tolist()  # Detectar outliers
    return {'min': float(min_val), 'q1': float(q1), 'median': float(median), 'q3': float(q3), 'max': float(max_val), 'outliers': outliers}

# Aplicar la función a cada categoría
var_x,var_y = 'categoria','variable'
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


