from .permissions import asignar_permisos_por_rol

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            asignar_permisos_por_rol(request.user)
        response = self.get_response(request)
        return response
