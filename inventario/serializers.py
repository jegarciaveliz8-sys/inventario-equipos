from rest_framework import serializers
from .models import (
    Equipo, Cliente, Accesorio, Asignacion,
    CambioReparacion, HojaResponsabilidad, Alerta, Evidencia, Notificacion
)


class EquipoSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    qr_url = serializers.CharField(source='qr_code.url', read_only=True)

    class Meta:
        model = Equipo
        fields = [
            'id', 'uuid', 'nombre', 'marca', 'modelo', 'serial',
            'descripcion', 'estado', 'estado_display', 'fecha_fin_garantia',
            'foto', 'qr_url', 'fecha_registro'
        ]


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'uuid', 'nombre', 'dpi', 'telefono', 'email', 'direccion', 'fecha_registro']


class AccesorioSerializer(serializers.ModelSerializer):
    stock_bajo = serializers.BooleanField(source='stock_bajo', read_only=True)

    class Meta:
        model = Accesorio
        fields = ['id', 'uuid', 'nombre', 'descripcion', 'cantidad', 'stock_minimo', 'stock_bajo']


class AsignacionSerializer(serializers.ModelSerializer):
    equipo_serial = serializers.CharField(source='equipo.serial', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)

    class Meta:
        model = Asignacion
        fields = [
            'id', 'uuid', 'equipo', 'equipo_serial', 'cliente', 'cliente_nombre',
            'fecha_asignacion', 'fecha_devolucion', 'observaciones', 'activa'
        ]


class CambioReparacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    equipo_serial = serializers.CharField(source='equipo.serial', read_only=True)

    class Meta:
        model = CambioReparacion
        fields = [
            'id', 'uuid', 'equipo', 'equipo_serial', 'tipo', 'tipo_display',
            'descripcion', 'tecnico', 'fecha', 'costo'
        ]


class HojaResponsabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = HojaResponsabilidad
        fields = [
            'id', 'uuid', 'asignacion', 'firmado', 'fecha_generacion',
            'fecha_firma', 'pdf_generado'
        ]


class AlertaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Alerta
        fields = [
            'id', 'uuid', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'fecha_creacion', 'equipo', 'accesorio'
        ]


class EvidenciaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    imagen_url = serializers.CharField(source='imagen.url', read_only=True)

    class Meta:
        model = Evidencia
        fields = [
            'id', 'uuid', 'equipo', 'tipo', 'tipo_display',
            'descripcion', 'imagen', 'imagen_url', 'fecha', 'subido_por'
        ]


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'id', 'uuid', 'tipo', 'destinatario', 'asunto',
            'mensaje', 'enviado', 'fecha_creacion'
        ]
