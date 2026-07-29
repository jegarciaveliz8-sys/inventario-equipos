from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

ROLES = {
    'tecnico': ['inventario.view_equipo', 'inventario.view_cliente', 'inventario.add_cambioreparacion'],
    'coordinador': ['inventario.view_equipo', 'inventario.add_asignacion', 'inventario.change_equipo', 'inventario.view_cliente'],
    'auditor': ['inventario.view_equipo', 'inventario.view_asignacion', 'inventario.view_cambioreparacion'],
    'admin': ['*'],
}

def asignar_permisos_por_rol(user):
    if not user.groups.exists():
        return
    grupo = user.groups.first().name.lower()
    permisos = ROLES.get(grupo, [])
    if '*' in permisos:
        return
    # Limpiar permisos actuales y asignar nuevos
    user.user_permissions.clear()
    from django.contrib.auth.models import Permission
    for codename in permisos:
        try:
            app_label, codename_only = codename.split('.')
            perm = Permission.objects.get(codename=codename_only, content_type__app_label=app_label)
            user.user_permissions.add(perm)
        except Permission.DoesNotExist:
            pass
