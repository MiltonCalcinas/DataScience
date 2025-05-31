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


from .models import UserTable
from .serializers import UserTableSerializer

def save_user_table(user, table_name):
    print("Guardando nombre de tabla del usuario")
    if not table_name:
        return None, {"table_name": "Este campo es requerido."}

    user_tables = UserTable.objects.filter(user=user)
    if user_tables.exists():
        db_name = user_tables.first().db_name
    else:
        db_name = f"db_for_{user.username}"

    data = {
        "table_name": table_name,
        "db_name": db_name,
    }

    serializer = UserTableSerializer(data=data)
    print("--- Nombre tabla serializando")
    if serializer.is_valid():
        serializer.save(user=user)
        print("--Nombre tabla  guardada")
        return serializer.data, None
    else:
        print("serializacino fallida")
        return None, serializer.errors





VAR_CONEXION_CLIENTE = {}
VAR_CONEXION_SERVIDOR = {
    "USER": "cliente",
    "PASSWORD": "cliente1234",
    "HOST": "localhost",
    "PUERTO": 3306,
    "DB": "db_clientes",
    "URL":  f"mysql+mysqlconnector://cliente:cliente1234@localhost/",
  
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






def importar_desde_db(data):
    pass


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
























