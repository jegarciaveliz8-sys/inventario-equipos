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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .utils.cloudinary_upload import subir_evidencia


class SubirEvidenciaAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        foto = request.FILES.get('foto')
        equipo_id = request.data.get('equipoId', 'equipo')

        if not foto:
            return Response(
                {'error': 'No se envio ninguna foto'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            url = subir_evidencia(foto, equipo_id)
            
            return Response({
                'success': True,
                'url': url,
                'mensaje': 'Evidencia guardada correctamente'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
