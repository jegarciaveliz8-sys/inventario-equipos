from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Equipo, Cliente, Accesorio, Asignacion, CambioReparacion,
    HojaResponsabilidad, Alerta, Evidencia, Notificacion,
    Sucursal, MantenimientoPreventivo
)


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'encargado', 'activa']
    search_fields = ['nombre', 'direccion']


@admin.register(Equipo)
class EquipoAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'serial', 'marca', 'estado_coloreado', 'sucursal', 'fecha_registro', 'acciones_estado']
    list_filter = ['estado', 'marca', 'sucursal', 'fecha_registro']
    search_fields = ['nombre', 'serial', 'marca', 'modelo']
    readonly_fields = ['uuid', 'qr_preview', 'fecha_registro', 'estado']
    fieldsets = (
        (None, {'fields': ('uuid', 'nombre', 'marca', 'modelo', 'serial', 'descripcion', 'estado', 'sucursal')}),
        ('Detalles', {'fields': ('fecha_fin_garantia', 'foto', 'qr_preview')}),
        ('Auditoria', {'fields': ('fecha_registro',)}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/accion/<str:accion>/', self.admin_site.admin_view(self.accion_estado), name='equipo_accion_estado'),
        ]
        return custom_urls + urls

    def accion_estado(self, request, object_id, accion):
        equipo = get_object_or_404(Equipo, pk=object_id)
        try:
            if accion == 'asignar' and equipo.estado == 'disponible':
                equipo.asignar(); equipo.save()
                messages.success(request, f'Equipo {equipo} marcado como Asignado.')
            elif accion == 'reparar' and equipo.estado == 'en_reparacion':
                equipo.reparar(); equipo.save()
                messages.success(request, f'Equipo {equipo} reparado.')
            elif accion == 'reportar_fallo' and equipo.estado == 'asignado':
                equipo.reportar_fallo(); equipo.save()
                messages.success(request, f'Equipo {equipo} en reparacion.')
            elif accion == 'dar_baja' and equipo.estado in ['disponible', 'en_reparacion']:
                equipo.dar_de_baja(); equipo.save()
                messages.success(request, f'Equipo {equipo} dado de baja.')
            else:
                messages.error(request, f'Transicion no permitida desde "{equipo.get_estado_display()}".')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect(reverse('admin:inventario_equipo_change', args=[object_id]))

    def estado_coloreado(self, obj):
        colores = {'disponible':'success','asignado':'primary','en_reparacion':'warning','dado_de_baja':'secondary'}
        return format_html('<span class="badge bg-{}">{}</span>', colores.get(obj.estado,'dark'), obj.get_estado_display())
    estado_coloreado.short_description = 'Estado'

    def acciones_estado(self, obj):
        btns = []
        if obj.estado == 'disponible':
            btns.append(f'<a class="button" href="{reverse("admin:equipo_accion_estado", args=[obj.pk,"asignar"])}">Asignar</a>')
            btns.append(f'<a class="button" href="{reverse("admin:equipo_accion_estado", args=[obj.pk,"dar_baja"])}">Dar Baja</a>')
        elif obj.estado == 'asignado':
            btns.append(f'<a class="button" href="{reverse("admin:equipo_accion_estado", args=[obj.pk,"reportar_fallo"])}">Reportar Fallo</a>')
        elif obj.estado == 'en_reparacion':
            btns.append(f'<a class="button" href="{reverse("admin:equipo_accion_estado", args=[obj.pk,"reparar"])}">Reparar</a>')
            btns.append(f'<a class="button" href="{reverse("admin:equipo_accion_estado", args=[obj.pk,"dar_baja"])}">Dar Baja</a>')
        return format_html(' '.join(btns))
    acciones_estado.short_description = 'Acciones'

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html('<a href="{}" target="_blank"><img src="{}" width="150" style="border:1px solid #ccc;" /></a><br><small>Click para ver en grande / escanear</small>', obj.qr_code.url, obj.qr_code.url)
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
    def stock_bajo(self, obj): return obj.stock_bajo()
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


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'tipo', 'descripcion', 'fecha', 'subido_por']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['asunto', 'destinatario', 'enviado', 'fecha_creacion']
    list_filter = ['enviado', 'tipo']
    readonly_fields = ['uuid']


@admin.register(MantenimientoPreventivo)
class MantenimientoPreventivoAdmin(SimpleHistoryAdmin):
    list_display = ['equipo', 'tipo', 'frecuencia_meses', 'proxima_fecha', 'completado']
    list_filter = ['tipo', 'completado']
    readonly_fields = ['uuid']
