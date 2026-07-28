from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Equipo, Cliente, Accesorio, Asignacion, CambioReparacion, HojaResponsabilidad, Alerta


@admin.register(Equipo)
class EquipoAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'serial', 'marca', 'estado', 'fecha_registro']
    list_filter = ['estado', 'marca', 'fecha_registro']
    search_fields = ['nombre', 'serial', 'marca', 'modelo']
    readonly_fields = ['uuid', 'qr_preview', 'fecha_registro']
    fieldsets = (
        (None, {'fields': ('uuid', 'nombre', 'marca', 'modelo', 'serial', 'descripcion', 'estado')}),
        ('Detalles', {'fields': ('fecha_fin_garantia', 'foto', 'qr_preview')}),
        ('Auditoria', {'fields': ('fecha_registro',)}),
    )

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="150" style="border:1px solid #ccc;" /></a>'
                '<br><small>Click para ver en grande / escanear</small>',
                obj.qr_code.url, obj.qr_code.url
            )
        return format_html('<span style="color:red;">Sin QR. Guarde el equipo para generarlo.</span>')
    qr_preview.short_description = 'Codigo QR'


@admin.register(Cliente)
class ClienteAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'dpi', 'telefono', 'email', 'fecha_registro']
    search_fields = ['nombre', 'dpi', 'email']
    readonly_fields = ['uuid']


@admin.register(Accesorio)
class AccesorioAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'cantidad', 'stock_minimo', 'stock_bajo']
    list_filter = ['cantidad']
    readonly_fields = ['uuid']

    def stock_bajo(self, obj):
        return obj.stock_bajo()
    stock_bajo.boolean = True


@admin.register(Asignacion)
class AsignacionAdmin(SimpleHistoryAdmin):
    list_display = ['equipo', 'cliente', 'fecha_asignacion', 'activa']
    list_filter = ['activa', 'fecha_asignacion']
    search_fields = ['equipo__nombre', 'equipo__serial', 'cliente__nombre']
    readonly_fields = ['uuid']


@admin.register(CambioReparacion)
class CambioReparacionAdmin(SimpleHistoryAdmin):
    list_display = ['equipo', 'tipo', 'tecnico', 'fecha', 'costo']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['uuid']


@admin.register(HojaResponsabilidad)
class HojaResponsabilidadAdmin(SimpleHistoryAdmin):
    list_display = ['asignacion', 'firmado', 'fecha_generacion', 'fecha_firma']
    list_filter = ['firmado']
    readonly_fields = ['uuid']


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'titulo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida']
    readonly_fields = ['uuid']
