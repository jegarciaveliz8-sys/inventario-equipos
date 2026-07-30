from rest_framework.routers import DefaultRouter
from .api_views import (
    EquipoViewSet, ClienteViewSet, AccesorioViewSet,
    AsignacionViewSet, CambioReparacionViewSet,
    HojaResponsabilidadViewSet, AlertaViewSet,
    EvidenciaViewSet, NotificacionViewSet
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

urlpatterns = router.urls
