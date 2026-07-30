from rest_framework import viewsets
from .models import (
    Equipo, Cliente, Accesorio, Asignacion,
    CambioReparacion, HojaResponsabilidad, Alerta, Evidencia, Notificacion
)
from .serializers import (
    EquipoSerializer, ClienteSerializer, AccesorioSerializer,
    AsignacionSerializer, CambioReparacionSerializer,
    HojaResponsabilidadSerializer, AlertaSerializer,
    EvidenciaSerializer, NotificacionSerializer
)


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    lookup_field = 'uuid'


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    lookup_field = 'uuid'


class AccesorioViewSet(viewsets.ModelViewSet):
    queryset = Accesorio.objects.all()
    serializer_class = AccesorioSerializer


class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()
    serializer_class = AsignacionSerializer


class CambioReparacionViewSet(viewsets.ModelViewSet):
    queryset = CambioReparacion.objects.all()
    serializer_class = CambioReparacionSerializer


class HojaResponsabilidadViewSet(viewsets.ModelViewSet):
    queryset = HojaResponsabilidad.objects.all()
    serializer_class = HojaResponsabilidadSerializer


class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer


class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = Evidencia.objects.all()
    serializer_class = EvidenciaSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
