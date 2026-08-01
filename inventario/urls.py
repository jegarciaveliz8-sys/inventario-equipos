from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('equipos/<uuid:uuid>/', views.EquipoFichaPublicaView.as_view(), name='equipo_ficha_publica'),
    path('escanear-qr/', views.escanear_qr, name='escanear_qr'),
    path('buscar/', views.busqueda_global, name='busqueda_global'),
    path('reportes/equipos/', views.reporte_equipos, name='reporte_equipos'),
    path('reporte/evidencias/pdf/', views.reporte_evidencias_pdf, name='reporte_evidencias_pdf'),
    path('evidencia/subir/', views.subir_evidencia, name='subir_evidencia'),
    path('evidencia/movil/', views.subir_evidencia_movil, name='subir_evidencia_movil'),
    path('metricas/', views.metricas_avanzadas, name='metricas'),
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('mantenimientos/<int:pk>/completar/', views.completar_mantenimiento, name='completar_mantenimiento'),
    path('licencias/', views.lista_licencias, name='lista_licencias'),
    path('hojas/<int:pk>/', views.pagina_firma, name='pagina_firma'),
    path('hojas/<int:pk>/pdf/', views.generar_pdf_hoja, name='generar_pdf_hoja'),
    path('hojas/<int:pk>/firmar/', views.firmar_hoja, name='firmar_hoja'),
    path('importar-equipos/', views.importar_equipos_excel, name='importar_equipos'),
    path('verificar-alertas/', views.verificar_alertas, name='verificar_alertas'),
    path('alertas/<int:pk>/leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),
    path('seed-licencias-mantenimientos/', views.seed_licencias_mantenimientos_web, name='seed_licencias_web'),
]
