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
    try:
        data = json.loads(request.body)
        columnas = data.get("columnas")
        estadistico =estadisticos[ data.get("estadistico")]
        df = obtener_df(request)
        return df[columnas].apply(estadistico).to_dict(),200
    except json.JSONDecodeError as e:
        return {"error": f"Error en los datos: {str(e)}"},400
    






"""   recibe un json con modelos: [lista de modelos], tipo: regr o cls  , var_dep: y , test_size, """
def realizar_entrenamiento(request):
    try:
        data = json.loads(request.body)
        modelos_elegidos = data.get("modelos")  # Nombre de los modelos
        tipo_modelo = data.get("tipo")
        variable_dependiente = data.get("variable_dependiente")  # Variable dependiente
        
        if tipo_modelo== "Regresion":
            scoring= "neg_mean_squared_error"
        else:
            scoring="precision"

        # Recuperar el DataFrame de la sesión
        df = obtener_df(request) 
        X = df.drop(columns=[variable_dependiente])
        y = df[variable_dependiente] 

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # realizar busqueda           
        if  not data.get("busqueda") :
            search,metricas =  busqueda(X_train,y_train,X_test,y_test,modelos_elegidos,data.get("params"),scoring,data.get("busqueda"))
            return {"busqueda":search,"metricas":metricas},200
        # metricas sin ajustar hiperparametros        
        metricas = {}
        for nombreModelo in modelos_elegidos:          
            modelo = modelos_dic[nombreModelo]
            modelo.fit(X_train, y_train)
            metrica = calcular_metricas(modelo,X_test,y_test,tipo_modelo)
            metricas[f"{nombreModelo}_metrica"] = metrica
        return metricas,200
    
    except json.JSONDecodeError as ex:
        return {"error": f"Error en los datos: {str(ex)}"},400
        
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"},500
    

def calcular_metricas(modelo,X_test,y_test,tipo_modelo):
    y_pred = modelo.predict(X_test)
    y_scores = modelo.predict_proba(X_test)[:,1]

    if tipo_modelo == "Regresion":
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        return {"mse":mse,"rmse":rmse,"R^2": r2}
    else:
        report = classification_report(y_true= y_test,y_pred=y_pred)
        matriz_confusion = confusion_matrix(y_true=y_test,y_pred=y_pred)
        fpr,tpr,_ = roc_curve(y_test,y_scores)
        auc_score = auc(fpr,tpr)
        return {"report":report,"matriz_confusion":matriz_confusion,"auc_score": auc_score}


def busqueda(X_train,y_train,X_test,y_test,modelos_elegidos,hiperparametros,scoring,busqueda):
    mejores_modelos= {}
    if busqueda == "GridSearchCV":
        for nombreModelo in modelos_elegidos:
            modelo = modelos_dic[nombreModelo]
            search = GridSearchCV(
                modelo,
                hiperparametros,
                cv=5,
                scoring=scoring,
                n_jobs=-1
            )
            search.fit(X_train,y_train)
            mejores_modelos[nombreModelo] ={"best_estamador": search.best_estimator_, 
                                            "best_params": search.best_params_,
                                           "best_score": search.best_score_}
    
    else:
        for nombreModelo in modelos_elegidos:
            modelo = modelos_dic[nombreModelo]
            search = RandomizedSearchCV(
                modelo,
                hiperparametros,
                cv=5,
                scoring=scoring,
                n_iter=5,
                n_jobs=-1
            )
            search.fit(X_train,y_train)
            mejores_modelos[nombreModelo] ={"best_estamador": search.best_estimator_, 
                                            "best_params": search.best_params_,
                                           "best_score": search.best_score_}
    
    metricas = {}
    for nombreModelo in mejores_modelos:
        modelo = mejores_modelos[nombreModelo].get("best_estamador")
        y_pred = modelo.predict(X_test)
        mse = mean_squared_error(y_test,y_pred)
        rmse = np.sqrt(mse)
        metricas[nombreModelo] = {"mse": mse, "rmse":rmse}

    return mejores_modelos,metricas




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


