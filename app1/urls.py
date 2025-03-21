from . import views
from django.urls import path
from django.shortcuts import render

urlpatterns= [
    path('',views.main,name='main'),
    path('cargar_datos/',views.cargar_datos,name='cargar_datos'),
    path('filtrar/',views.filtrar,name='filtrar'),
    path('elegir_columnas/',views.elegir_columnas,name='elegir_columnas'),
    path('elegir_filas/',views.elegir_filas,name='elegir_filas'),
    path('transformar_vars/',views.transformar_variables,name='transformar_vars'),
    path('generar_grafico/', views.generar_grafico, name='generar_grafico'),
    path('generar_estadistico/', views.generar_estadistico, name='generar_estadistico'),
    path('entrenar_modelo/',views.entrenar_modelo,name='entrenar_modelo'),
    path('nombre_columnas/',views.get_columns_name,name='nombre_columnas'),
]