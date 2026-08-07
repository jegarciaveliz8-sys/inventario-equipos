from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Equipo, Cliente, Accesorio, Asignacion, CambioReparacion,
    HojaResponsabilidad, Alerta, Evidencia, Notificacion,
    Ubicacion, Categoria, SoftwareLicencia, MantenimientoPreventivo
)


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'responsable', 'activa', 'num_equipos']
    list_filter = ['activa']
    search_fields = ['nombre', 'responsable']

    def num_equipos(self, obj):
        return obj.equipos.count()
    num_equipos.short_description = 'Equipos'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'num_equipos']
    search_fields = ['nombre']

    def num_equipos(self, obj):
        return obj.equipos.count()
    num_equipos.short_description = 'Equipos'


@admin.register(SoftwareLicencia)
class SoftwareLicenciaAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'equipo', 'tipo', 'fecha_vencimiento', 'dias_para_vencer', 'activa']
    list_filter = ['tipo', 'activa', 'fecha_vencimiento']
    search_fields = ['nombre', 'equipo__nombre', 'equipo__serial', 'clave']
    readonly_fields = ['uuid', 'dias_para_vencer']
    date_hierarchy = 'fecha_vencimiento'

    def dias_para_vencer(self, obj):
        dias = obj.dias_para_vencer()
        if dias is None:
            return format_html('<span style="color:gray;">Sin fecha</span>')
        if dias < 0:
            return format_html('<span style="color:red; font-weight:bold;">Vencida ({} dias)</span>', abs(dias))
        if dias <= 30:
            return format_html('<span style="color:orange; font-weight:bold;">{} dias</span>', dias)
        return format_html('<span style="color:green;">{} dias</span>', dias)
    dias_para_vencer.short_description = 'Dias restantes'


@admin.register(MantenimientoPreventivo)
class MantenimientoPreventivoAdmin(SimpleHistoryAdmin):
    list_display = ['titulo', 'equipo', 'frecuencia', 'proxima_fecha', 'completado', 'esta_vencido']
    list_filter = ['frecuencia', 'completado', 'proxima_fecha']
    search_fields = ['titulo', 'equipo__nombre', 'equipo__serial', 'tecnico']
    readonly_fields = ['uuid', 'calcular_proxima_fecha']
    date_hierarchy = 'proxima_fecha'
    actions = ['marcar_completado']

    def esta_vencido(self, obj):
        if obj.esta_vencido():
            return format_html('<span style="color:red; font-weight:bold;">VENCIDO</span>')
        dias = obj.dias_para_vencer()
        if dias is not None and dias <= 7:
            return format_html('<span style="color:orange; font-weight:bold;">URGENTE</span>')
        return format_html('<span style="color:green;">OK</span>')
    esta_vencido.short_description = 'Estado'

    @admin.action(description='Marcar mantenimientos seleccionados como completados')
    def marcar_completado(self, request, queryset):
        for mp in queryset:
            mp.completado = True
            mp.ultima_fecha = timezone.now().date()
            mp.proxima_fecha = mp.calcular_proxima_fecha()
            mp.save()
        self.message_user(request, f'{queryset.count()} mantenimientos marcados como completados.')


@admin.register(Equipo)
class EquipoAdmin(SimpleHistoryAdmin):
    list_display = ['nombre', 'serial', 'marca', 'categoria', 'ubicacion', 'estado_coloreado', 'fecha_registro', 'acciones_estado']
    list_filter = ['estado', 'marca', 'categoria', 'ubicacion', 'fecha_registro']
    search_fields = ['nombre', 'serial', 'marca', 'modelo']
    readonly_fields = ['uuid', 'qr_preview', 'fecha_registro', 'estado']
    fieldsets = (
        (None, {'fields': ('uuid', 'nombre', 'categoria', 'marca', 'modelo', 'serial', 'descripcion', 'estado')}),
        ('Ubicacion', {'fields': ('ubicacion',)}),
        ('Detalles', {'fields': ('fecha_fin_garantia', 'foto', 'qr_preview')}),
        ('Auditoria', {'fields': ('fecha_registro',)}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['categoria'].required = True
        form.base_fields['ubicacion'].required = True
        return form

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
        return format_html('<span class="badge bg-{}" style="padding:6px 10px; font-size:12px;">{}</span>', colores.get(obj.estado,'dark'), obj.get_estado_display())
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
    list_display = ['equipo', 'cliente', 'ubicacion', 'fecha_asignacion', 'activa']
    list_filter = ['activa', 'fecha_asignacion', 'ubicacion']
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
    readonly_fields = ['uuid', 'qr_equipo_preview', 'firma_preview']
    
    def qr_equipo_preview(self, obj):
        equipo = obj.asignacion.equipo if obj.asignacion else None
        if equipo and equipo.qr_code:
            return format_html(
                '<div style="text-align:center;">'
                '<img src="{}" width="180" style="border:1px solid #ddd; padding:5px; border-radius:4px;"/>'
                '<p style="margin-top:5px; color:#666; font-size:11px;">Escanea para ver ficha del equipo</p>'
                '</div>',
                equipo.qr_code.url
            )
        return format_html('<p style="color:red;">⚠️ El equipo no tiene QR</p>')
    qr_equipo_preview.short_description = 'QR del Equipo'
    
    def firma_preview(self, obj):
        if obj.firma_imagen:
            return format_html('<img src="{}" width="300" style="border:1px solid #ccc;"/>', obj.firma_imagen.url)
        return format_html('<span style="color:gray;">Sin firma digital</span>')
    firma_preview.short_description = 'Firma Digital'


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'titulo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida']
    readonly_fields = ['uuid']
    actions = ['marcar_leidas']

    @admin.action(description='Marcar alertas seleccionadas como leidas')
    def marcar_leidas(self, request, queryset):
        queryset.update(leida=True)
        self.message_user(request, f'{queryset.count()} alertas marcadas como leidas.')


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'tipo', 'descripcion', 'fecha', 'subido_por']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['asunto', 'destinatario', 'enviado', 'fecha_creacion']
    list_filter = ['enviado', 'tipo']
    readonly_fields = ['uuid']
