from django.contrib import admin
from .models import Equipo, Cliente, Accesorio, Asignacion, CambioReparacion, HojaResponsabilidad


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'modelo', 'serial', 'estado', 'fecha_registro']
    list_filter = ['estado', 'marca']
    search_fields = ['nombre', 'serial', 'modelo']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'dpi', 'telefono', 'fecha_registro']
    search_fields = ['nombre', 'dpi', 'telefono']


@admin.register(Accesorio)
class AccesorioAdmin(admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'cliente', 'fecha_asignacion', 'activa']
    list_filter = ['activa', 'fecha_asignacion']
    filter_horizontal = ['accesorios_entregados']


@admin.register(CambioReparacion)
class CambioReparacionAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'tipo', 'tecnico', 'fecha', 'costo']
    list_filter = ['tipo', 'fecha']


@admin.register(HojaResponsabilidad)
class HojaResponsabilidadAdmin(admin.ModelAdmin):
    list_display = ['id', 'asignacion', 'firmado', 'fecha_firma', 'fecha_generacion']
    list_filter = ['firmado', 'fecha_generacion']
    readonly_fields = ['fecha_generacion', 'fecha_firma', 'firmado']
