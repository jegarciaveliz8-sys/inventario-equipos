import json
import openpyxl
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView, TemplateView
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta
from weasyprint import HTML
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Equipo, Cliente, Asignacion, CambioReparacion, HojaResponsabilidad, Accesorio, Alerta


# ─── DASHBOARD ───────────────────────────────────────────────

class DashboardView(TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_equipos'] = Equipo.objects.count()
        ctx['asignados'] = Equipo.objects.filter(estado='asignado').count()
        ctx['en_reparacion'] = Equipo.objects.filter(estado='en_reparacion').count()
        ctx['disponibles'] = Equipo.objects.filter(estado='disponible').count()
        ctx['clientes'] = Cliente.objects.count()
        ctx['asignaciones_activas'] = Asignacion.objects.filter(activa=True).count()
        ctx['hojas_pendientes'] = HojaResponsabilidad.objects.filter(firmado=False).count()
        ctx['alertas'] = Alerta.objects.filter(leida=False)[:5]
        ctx['stock_bajo'] = [a for a in Accesorio.objects.all() if a.stock_bajo()]
        return ctx


# ─── API DASHBOARD (Chart.js) ────────────────────────────────

@api_view(['GET'])
def dashboard_stats_api(request):
    hoy = timezone.now()
    total = Equipo.objects.count()
    asignados = Equipo.objects.filter(estado='asignado').count()
    en_reparacion = Equipo.objects.filter(estado='en_reparacion').count()
    disponibles = Equipo.objects.filter(estado='disponible').count()
    dado_baja = Equipo.objects.filter(estado='dado_de_baja').count()

    por_marca = list(Equipo.objects.values('marca').annotate(total=Count('id')).order_by('-total')[:8])

    asignaciones_mes = []
    for i in range(5, -1, -1):
        mes = hoy - relativedelta(months=i)
        count = Asignacion.objects.filter(
            fecha_asignacion__year=mes.year,
            fecha_asignacion__month=mes.month
        ).count()
        asignaciones_mes.append({'mes': mes.strftime('%b %Y'), 'total': count})

    reparaciones_tipo = list(CambioReparacion.objects.values('tipo').annotate(total=Count('id')))

    return Response({
        'totales': {
            'total': total,
            'asignados': asignados,
            'reparacion': en_reparacion,
            'disponibles': disponibles,
            'baja': dado_baja
        },
        'por_marca': por_marca,
        'asignaciones_trend': asignaciones_mes,
        'reparaciones_tipo': reparaciones_tipo,
    })


# ─── FICHA PUBLICA POR QR ────────────────────────────────────

class EquipoFichaPublicaView(DetailView):
    model = Equipo
    template_name = 'inventario/equipo_ficha.html'
    context_object_name = 'equipo'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['asignacion_actual'] = self.object.asignaciones.filter(activa=True).first()
        ctx['historial_reparaciones'] = self.object.cambios.all()[:10]
        ctx['historial_completo'] = self.object.history.all()[:10]
        return ctx


# ─── GENERAR PDF HOJA RESPONSABILIDAD ────────────────────────

@staff_member_required
def generar_pdf_hoja(request, pk):
    hoja = get_object_or_404(HojaResponsabilidad, pk=pk)
    html_string = render_to_string('reportes/hoja_responsabilidad.html', {
        'hoja': hoja,
        'asignacion': hoja.asignacion,
        'equipo': hoja.asignacion.equipo,
        'cliente': hoja.asignacion.cliente,
        'fecha': timezone.now(),
    })
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=hoja_{hoja.asignacion.equipo.serial}.pdf'
    return response


# ─── FIRMA DIGITAL (CANVAS) ──────────────────────────────────

@require_POST
def firmar_hoja(request, pk):
    hoja = get_object_or_404(HojaResponsabilidad, pk=pk)
    import base64
    from django.core.files.base import ContentFile

    data = json.loads(request.body)
    firma_data = data.get('firma')
    if firma_data:
        format, imgstr = firma_data.split(';base64,')
        ext = format.split('/')[-1]
        hoja.firma_imagen.save(f'firma_{hoja.id}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
        hoja.firmado = True
        hoja.fecha_firma = timezone.now()
        hoja.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'No se recibio firma'})


# ─── IMPORTACION MASIVA EXCEL ────────────────────────────────

@staff_member_required
def importar_equipos_excel(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, 'No se selecciono archivo')
            return redirect('admin:inventario_equipo_changelist')

        wb = openpyxl.load_workbook(archivo)
        ws = wb.active
        creados = 0
        errores = []

        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                nombre, marca, modelo, serial = row[0], row[1], row[2], row[3]
                if not serial:
                    continue
                Equipo.objects.create(
                    nombre=nombre or 'Sin nombre',
                    marca=marca or '',
                    modelo=modelo or '',
                    serial=str(serial)
                )
                creados += 1
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        messages.success(request, f'{creados} equipos importados correctamente.')
        if errores:
            messages.warning(request, f'Errores en {len(errores)} filas. Primeros: {", ".join(errores[:3])}')
        return redirect('admin:inventario_equipo_changelist')

    return render(request, 'admin/importar_equipos.html')


# ─── VERIFICAR ALERTAS ───────────────────────────────────────

@staff_member_required
def verificar_alertas(request):
    hoy = timezone.now().date()
    creadas = 0
    from datetime import timedelta

    # Garantias por vencer (30 dias)
    for eq in Equipo.objects.filter(
        fecha_fin_garantia__lte=hoy + timedelta(days=30),
        fecha_fin_garantia__gte=hoy,
        estado__in=['disponible', 'asignado']
    ):
        alerta, c = Alerta.objects.get_or_create(
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
            alerta, c = Alerta.objects.get_or_create(
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
                alerta, c = Alerta.objects.get_or_create(
                    tipo='revision',
                    equipo=asig.equipo,
                    defaults={
                        'titulo': f'Revision pendiente: {asig.equipo}',
                        'mensaje': f'El equipo {asig.equipo} asignado a {asig.cliente} lleva mas de 1 ano sin revision.'
                    }
                )
                if c:
                    creadas += 1

    messages.success(request, f'Se verificaron alertas. {creadas} nuevas creadas.')
    return redirect('dashboard')


# ─── MARCAR ALERTA LEIDA ─────────────────────────────────────

@require_POST
def marcar_alerta_leida(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk)
    alerta.leida = True
    alerta.save()
    return JsonResponse({'ok': True})
