from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventario.models import MantenimientoPreventivo, Alerta

class Command(BaseCommand):
    help = 'Verifica mantenimientos preventivos proximos'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        proximos_7 = hoy + timedelta(days=7)
        creadas = 0

        for mp in MantenimientoPreventivo.objects.filter(completado=False):
            if mp.proxima_fecha and mp.proxima_fecha <= proximos_7:
                _, c = Alerta.objects.get_or_create(
                    tipo='general',
                    equipo=mp.equipo,
                    defaults={
                        'titulo': f'Mantenimiento proximo: {mp.equipo}',
                        'mensaje': f'El equipo {mp.equipo} requiere {mp.get_tipo_display()} el {mp.proxima_fecha}.'
                    }
                )
                if c:
                    creadas += 1

        self.stdout.write(self.style.SUCCESS(f'{creadas} alertas de mantenimiento creadas.'))
