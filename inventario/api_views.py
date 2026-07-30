from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
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
from .utils.cloudinary_upload import subir_evidencia


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


class SubirEvidenciaAPIView(APIView):
    """
    POST /api/evidencias/subir/
    Sube foto a Cloudinary y guarda el registro en la base de datos
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        foto = request.FILES.get('foto')
        equipo_id = request.data.get('equipoId')
        tipo = request.data.get('tipo', 'general')
        descripcion = request.data.get('descripcion', '')

        # Validaciones
        if not foto:
            return Response(
                {'error': 'No se envio ninguna foto'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not equipo_id:
            return Response(
                {'error': 'Debes enviar equipoId'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar el equipo: primero por SERIAL (string), luego por ID (numero)
            equipo = None
            
            # 1. Intentar por serial
            try:
                equipo = Equipo.objects.get(serial=equipo_id)
            except Equipo.DoesNotExist:
                pass
            
            # 2. Si no, intentar por id (solo si es numero)
            if not equipo:
                try:
                    equipo_id_num = int(equipo_id)
                    equipo = Equipo.objects.get(id=equipo_id_num)
                except (ValueError, Equipo.DoesNotExist):
                    pass
            
            # 3. Si no se encontro
            if not equipo:
                return Response(
                    {'error': f'No existe equipo con ID o Serial: {equipo_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Subir a Cloudinary
            url = subir_evidencia(foto, str(equipo_id))

            # Crear el registro en la base de datos
            evidencia = Evidencia.objects.create(
                equipo=equipo,
                tipo=tipo,
                url_cloudinary=url,
                descripcion=descripcion,
                subido_por=request.user if request.user.is_authenticated else None
            )

            return Response({
                'success': True,
                'url': url,
                'evidencia_id': str(evidencia.uuid),
                'equipo': str(equipo),
                'mensaje': 'Evidencia guardada correctamente en Cloudinary y base de datos'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
