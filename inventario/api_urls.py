from rest_framework.routers import DefaultRouter
from .api_views import (
    EquipoViewSet, ClienteViewSet, AccesorioViewSet,
    AsignacionViewSet, CambioReparacionViewSet,
    HojaResponsabilidadViewSet, AlertaViewSet,
    EvidenciaViewSet, NotificacionViewSet
)

router = DefaultRouter()
router.register(r'equipos', EquipoViewSet, basename='api-equipos')
router.register(r'clientes', ClienteViewSet, basename='api-clientes')
router.register(r'accesorios', AccesorioViewSet, basename='api-accesorios')
router.register(r'asignaciones', AsignacionViewSet, basename='api-asignaciones')
router.register(r'reparaciones', CambioReparacionViewSet, basename='api-reparaciones')
router.register(r'hojas', HojaResponsabilidadViewSet, basename='api-hojas')
router.register(r'alertas', AlertaViewSet, basename='api-alertas')
router.register(r'evidencias', EvidenciaViewSet, basename='api-evidencias')
router.register(r'notificaciones', NotificacionViewSet, basename='api-notificaciones')

urlpatterns = router.urls
