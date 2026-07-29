from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('equipos/<uuid:uuid>/', views.EquipoFichaPublicaView.as_view(), name='equipo_ficha_publica'),
    path('escanear-qr/', views.escanear_qr, name='escanear_qr'),
    path('buscar/', views.busqueda_global, name='busqueda_global'),
    path('reportes/equipos/', views.reporte_equipos, name='reporte_equipos'),
    path('evidencia/subir/', views.subir_evidencia, name='subir_evidencia'),
    path('metricas/', views.metricas_avanzadas, name='metricas'),
    path('hojas/<int:pk>/', views.pagina_firma, name='pagina_firma'),
    path('hojas/<int:pk>/pdf/', views.generar_pdf_hoja, name='generar_pdf_hoja'),
    path('hojas/<int:pk>/firmar/', views.firmar_hoja, name='firmar_hoja'),
    path('importar-equipos/', views.importar_equipos_excel, name='importar_equipos'),
    path('verificar-alertas/', views.verificar_alertas, name='verificar_alertas'),
    path('alertas/<int:pk>/leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),
]
