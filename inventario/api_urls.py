from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    EquipoViewSet, ClienteViewSet, AccesorioViewSet,
    AsignacionViewSet, CambioReparacionViewSet,
    HojaResponsabilidadViewSet, AlertaViewSet,
    EvidenciaViewSet, NotificacionViewSet,
    SubirEvidenciaAPIView, ReporteEvidenciasAPIView
)

router = DefaultRouter()
router.register(r'equipos', EquipoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'accesorios', AccesorioViewSet)
router.register(r'asignaciones', AsignacionViewSet)
router.register(r'reparaciones', CambioReparacionViewSet)
router.register(r'hojas', HojaResponsabilidadViewSet)
router.register(r'alertas', AlertaViewSet)
router.register(r'evidencias', EvidenciaViewSet)
router.register(r'notificaciones', NotificacionViewSet)

urlpatterns = [
    path('evidencias/subir/', SubirEvidenciaAPIView.as_view(), name='subir_evidencia'),
    path('evidencias/reporte/', ReporteEvidenciasAPIView.as_view(), name='reporte_evidencias'),
    path('', include(router.urls)),
]
