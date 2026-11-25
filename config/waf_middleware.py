import logging
from django.http import HttpResponseForbidden

logger = logging.getLogger("django.security")

class CloudWAFMiddleware:
    RUTAS_BLOQUEADAS = ("/.env", "/.git", "/wp-admin", "/phpmyadmin", "/config.php", "/etc/passwd")
    AGENTES_BLOQUEADOS = ("sqlmap", "nikto", "masscan", "zgrab", "dirbuster", "gobuster")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ruta = request.path.lower()
        agente = request.META.get("HTTP_USER_AGENT", "").lower()
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown"))

        if any(r in ruta for r in self.RUTAS_BLOQUEADAS) or any(a in agente for a in self.AGENTES_BLOQUEADOS):
            logger.warning(f"[WAF BLOCK] Amenaza bloqueada | IP: {ip} | Ruta: {request.path} | UA: {agente}")
            return HttpResponseForbidden("403 Forbidden - Acceso bloqueado por politica de seguridad.")

        return self.get_response(request)
