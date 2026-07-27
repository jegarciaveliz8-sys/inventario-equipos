from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('equipos/', views.equipo_list, name='equipo_list'),
    path('equipos/<int:equipo_id>/', views.equipo_detail, name='equipo_detail'),
    path('asignaciones/', views.asignacion_list, name='asignacion_list'),
    path('asignaciones/nueva/', views.asignacion_nueva, name='asignacion_nueva'),
    path('hoja/<int:hoja_id>/firmar/', views.firmar_hoja, name='firmar_hoja'),
    path('hoja/<int:hoja_id>/guardar-firma/', views.guardar_firma, name='guardar_firma'),
    path('hoja/<int:hoja_id>/pdf/', views.descargar_pdf, name='descargar_pdf'),
]
