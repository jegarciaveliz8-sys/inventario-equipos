from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventario.models import Equipo, Accesorio, Asignacion, Alerta


class Command(BaseCommand):
    help = 'Verifica y crea alertas de garantias, stock bajo y revisiones pendientes'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        creadas = 0

        # Garantias por vencer (30 dias)
        for eq in Equipo.objects.filter(
            fecha_fin_garantia__lte=hoy + timedelta(days=30),
            fecha_fin_garantia__gte=hoy,
            estado__in=['disponible', 'asignado']
        ):
            _, c = Alerta.objects.get_or_create(
                tipo='garantia',
                equipo=eq,
                defaults={
                    'titulo': f'Garantia por vencer: {eq}',
                    'mensaje': f'La garantia del equipo {eq} vence el {eq.fecha_fin_garantia}.'
                }
            )
            if c:
                creadas += 1

        # Stock bajo
        for acc in Accesorio.objects.all():
            if acc.stock_bajo():
                _, c = Alerta.objects.get_or_create(
                    tipo='stock',
                    accesorio=acc,
                    defaults={
                        'titulo': f'Stock bajo: {acc.nombre}',
                        'mensaje': f'El accesorio {acc.nombre} tiene {acc.cantidad} unidades (minimo {acc.stock_minimo}).'
                    }
                )
                if c:
                    creadas += 1

        # Revisiones pendientes
        hace_un_ano = hoy - timedelta(days=365)
        for asig in Asignacion.objects.filter(activa=True):
            fecha_asig = asig.fecha_asignacion.date() if hasattr(asig.fecha_asignacion, 'date') else asig.fecha_asignacion
            if fecha_asig <= hace_un_ano:
                if not asig.ultima_revision or asig.ultima_revision < hace_un_ano:
                    _, c = Alerta.objects.get_or_create(
                        tipo='revision',
                        equipo=asig.equipo,
                        defaults={
                            'titulo': f'Revision pendiente: {asig.equipo}',
                            'mensaje': f'El equipo {asig.equipo} asignado a {asig.cliente} lleva mas de 1 ano sin revision.'
                        }
                    )
                    if c:
                        creadas += 1

        self.stdout.write(self.style.SUCCESS(f'Se crearon {creadas} alertas nuevas.'))
