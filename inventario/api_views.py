from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'marca']
    search_fields = ['nombre', 'serial', 'marca', 'modelo']
    ordering_fields = ['fecha_registro', 'nombre']
    lookup_field = 'uuid'


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'dpi', 'email', 'telefono']
    lookup_field = 'uuid'


class AccesorioViewSet(viewsets.ModelViewSet):
    queryset = Accesorio.objects.all()
    serializer_class = AccesorioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cantidad']


class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()
    serializer_class = AsignacionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activa', 'equipo', 'cliente']
    search_fields = ['equipo__serial', 'cliente__nombre']


class CambioReparacionViewSet(viewsets.ModelViewSet):
    queryset = CambioReparacion.objects.all()
    serializer_class = CambioReparacionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'equipo']


class HojaResponsabilidadViewSet(viewsets.ModelViewSet):
    queryset = HojaResponsabilidad.objects.all()
    serializer_class = HojaResponsabilidadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['firmado']


class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'leida']


class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = Evidencia.objects.all()
    serializer_class = EvidenciaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'equipo']


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enviado', 'tipo']
