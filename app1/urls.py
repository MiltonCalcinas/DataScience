from . import views
from django.urls import path
from django.shortcuts import render
from .views import SignupView, SigninView
from .views import VerifyTokenView
urlpatterns= [
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('main/',views.main,name='main'),
    path('signout/',views.signout,name='signout'),
    path('signin/',views.signin,name='signin'),
    path('create_task/',views.create_task,name='create_task'),
    path('cargar_datos/',views.cargar_datos,name='cargar_datos'),
    path('filtrar/',views.filtrar,name='filtrar'),
    path('elegir_columnas/',views.elegir_columnas,name='elegir_columnas'),
    path('transformar_vars/',views.transformar_variables,name='transformar_vars'),
    path('obtener_datos_grafico/', views.obtener_datos_grafico, name='obtener_datos_grafico'),
    path('generar_estadistico/', views.generar_estadistico, name='generar_estadistico'),
    path('entrenar_modelo/',views.entrenar_modelo,name='entrenar_modelo'),
    path('nombre_columnas/',views.get_columns_name,name='nombre_columnas'),
    path('api/signup/', SignupView.as_view(), name='api_signup'),
    path('api/signin/', SigninView.as_view(), name='api_signin'),
    path('api/verify_token/', VerifyTokenView.as_view()),
    path("api/save_tabla_name/", views.save_table_name, name="guardar_tabla"),
    path("api/last_table/", views.get_last_table, name="ultima_tabla"),
    path('api/table_name/', views.table_name_list, name='nombre_tablas_usuario'),
]