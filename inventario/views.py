import base64
import io
import os
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

from .models import Equipo, Cliente, Asignacion, HojaResponsabilidad, Accesorio


def dashboard(request):
    total_equipos = Equipo.objects.count()
    equipos_asignados = Equipo.objects.filter(estado='asignado').count()
    total_clientes = Cliente.objects.count()
    asignaciones_activas = Asignacion.objects.filter(activa=True).count()
    hojas_pendientes = HojaResponsabilidad.objects.filter(firmado=False).count()
    return render(request, 'inventario/dashboard.html', {
        'total_equipos': total_equipos,
        'equipos_asignados': equipos_asignados,
        'total_clientes': total_clientes,
        'asignaciones_activas': asignaciones_activas,
        'hojas_pendientes': hojas_pendientes,
    })


def equipo_list(request):
    equipos = Equipo.objects.all()
    return render(request, 'inventario/equipo_list.html', {'equipos': equipos})


def equipo_detail(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    historial = equipo.asignaciones.select_related('cliente').all()
    cambios = equipo.cambios.all()
    return render(request, 'inventario/equipo_detail.html', {
        'equipo': equipo,
        'historial': historial,
        'cambios': cambios,
    })


def asignacion_list(request):
    asignaciones = Asignacion.objects.select_related('equipo', 'cliente').all()
    return render(request, 'inventario/asignacion_list.html', {'asignaciones': asignaciones})


def asignacion_nueva(request):
    if request.method == 'POST':
        equipo_id = request.POST.get('equipo')
        cliente_id = request.POST.get('cliente')
        observaciones = request.POST.get('observaciones', '')
        accesorios_ids = request.POST.getlist('accesorios')

        equipo = get_object_or_404(Equipo, id=equipo_id)
        cliente = get_object_or_404(Cliente, id=cliente_id)

        asignacion = Asignacion.objects.create(
            equipo=equipo,
            cliente=cliente,
            observaciones=observaciones,
        )

        if accesorios_ids:
            asignacion.accesorios_entregados.set(accesorios_ids)

        equipo.estado = 'asignado'
        equipo.save()

        HojaResponsabilidad.objects.create(asignacion=asignacion)

        return redirect('inventario:asignacion_list')

    equipos = Equipo.objects.filter(estado='disponible')
    clientes = Cliente.objects.all()
    accesorios = Accesorio.objects.all()

    return render(request, 'inventario/asignacion_form.html', {
        'equipos': equipos,
        'clientes': clientes,
        'accesorios': accesorios,
    })


def firmar_hoja(request, hoja_id):
    hoja = get_object_or_404(HojaResponsabilidad, id=hoja_id)
    return render(request, 'inventario/firmar.html', {'hoja': hoja})


@csrf_exempt
def guardar_firma(request, hoja_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)

    hoja = get_object_or_404(HojaResponsabilidad, id=hoja_id)

    try:
        data = request.POST.get('firma')
        if not data:
            return JsonResponse({'success': False, 'error': 'No se recibio firma'})

        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        archivo = ContentFile(base64.b64decode(imgstr), name=f'firma_{hoja_id}.{ext}')

        hoja.firma_imagen = archivo
        hoja.firmado = True
        hoja.fecha_firma = datetime.now()
        hoja.save()

        generar_pdf_hoja(hoja)

        return JsonResponse({'success': True, 'message': 'Firma guardada correctamente'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def descargar_pdf(request, hoja_id):
    hoja = get_object_or_404(HojaResponsabilidad, id=hoja_id)

    if not hoja.pdf_generado:
        generar_pdf_hoja(hoja)

    if hoja.pdf_generado:
        response = HttpResponse(hoja.pdf_generado, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="hoja_responsabilidad_{hoja.id}.pdf"'
        return response

    return HttpResponse("PDF no disponible", status=404)


def generar_pdf_hoja(hoja):
    asignacion = hoja.asignacion
    equipo = asignacion.equipo
    cliente = asignacion.cliente

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#1a1a2e')
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor('#764ba2')
    )
    normal_style = styles["Normal"]
    normal_style.fontSize = 11
    normal_style.leading = 14

    story = []

    story.append(Paragraph("HOJA DE RESPONSABILIDAD", titulo_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(f"<b>Folio:</b> HR-{hoja.id:05d} &nbsp;&nbsp; <b>Fecha:</b> {hoja.fecha_generacion.strftime('%d/%m/%Y')}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("DATOS DEL RESPONSABLE", subtitulo_style))
    datos_cliente = [
        ['Nombre:', cliente.nombre],
        ['DPI/ID:', cliente.dpi or 'N/A'],
        ['Telefono:', cliente.telefono or 'N/A'],
        ['Direccion:', cliente.direccion or 'N/A'],
    ]
    t_cliente = Table(datos_cliente, colWidths=[1.5*inch, 4*inch])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cliente)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("DATOS DEL EQUIPO", subtitulo_style))
    datos_equipo = [
        ['Equipo:', equipo.nombre],
        ['Marca:', equipo.marca or 'N/A'],
        ['Modelo:', equipo.modelo or 'N/A'],
        ['Serial:', equipo.serial],
        ['Descripcion:', equipo.descripcion or 'N/A'],
    ]
    t_equipo = Table(datos_equipo, colWidths=[1.5*inch, 4*inch])
    t_equipo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_equipo)
    story.append(Spacer(1, 0.3*inch))

    accesorios = asignacion.accesorios_entregados.all()
    if accesorios:
        story.append(Paragraph("ACCESORIOS ENTREGADOS", subtitulo_style))
        acc_list = [[a.nombre] for a in accesorios]
        t_acc = Table(acc_list, colWidths=[5.5*inch])
        t_acc.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_acc)
        story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("CONDICIONES", subtitulo_style))
    story.append(Paragraph(hoja.condiciones, normal_style))
    story.append(Spacer(1, 0.4*inch))

    if hoja.firmado and hoja.firma_imagen:
        story.append(Paragraph("FIRMA DEL RESPONSABLE", subtitulo_style))
        firma_path = os.path.join(settings.MEDIA_ROOT, hoja.firma_imagen.name)
        if os.path.exists(firma_path):
            img = RLImage(firma_path, width=3*inch, height=1.2*inch)
            story.append(img)
        story.append(Paragraph(f"<b>Firmado el:</b> {hoja.fecha_firma.strftime('%d/%m/%Y %H:%M') if hoja.fecha_firma else 'N/A'}", normal_style))
    else:
        story.append(Paragraph("<i>Documento pendiente de firma</i>", normal_style))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<b>Nota:</b> Este documento tiene valor legal como constancia de entrega y responsabilidad del equipo descrito.", styles['Italic']))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    hoja.pdf_generado.save(f'hoja_{hoja.id}.pdf', ContentFile(pdf))
    hoja.save()
