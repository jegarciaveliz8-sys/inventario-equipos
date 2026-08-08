from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from inventario.models import (
    Equipo, Categoria, Ubicacion, Cliente, Asignacion,
    SoftwareLicencia, MantenimientoPreventivo, Accesorio,
    CambioReparacion, HojaResponsabilidad, Notificacion,
    Alerta, Evidencia
)

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos iniciales permanentes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('🚀 Iniciando carga de datos permanentes...'))

        # ============================================
        # 1. UBICACIONES (12)
        # ============================================
        ubis = [
            ('Oficina Principal', 'Oficina central de operaciones', 'Admin'),
            ('Sala de Servidores', 'Servidores y equipos de red', 'Admin Sistemas'),
            ('Bodega', 'Almacenamiento de equipos y repuestos', 'Almacen'),
            ('Recepcion', 'Atencion al publico', 'Recepcionista'),
            ('Sala de Juntas', 'Reuniones y videoconferencias', 'Coordinador'),
            ('Area de Desarrollo', 'Estaciones de programacion', 'Lider Dev'),
            ('Area Contable', 'Contabilidad y finanzas', 'Jefe Contable'),
            ('Sala de Capacitacion', 'Capacitaciones y talleres', 'Coordinador de Capacitacion'),
            ('Home Office', 'Trabajo remoto', 'N/A'),
            ('Sala de Soporte', 'Soporte tecnico y atencion', 'Jefe de Soporte'),
            ('Cafeteria', 'Area de descanso', 'Admin'),
            ('Garita de Seguridad', 'Control de accesos', 'Seguridad'),
        ]
        for n, d, r in ubis:
            Ubicacion.objects.get_or_create(nombre=n, defaults={'descripcion': d, 'responsable': r, 'activa': True})
        self.stdout.write(self.style.SUCCESS(f'✅ {Ubicacion.objects.count()} ubicaciones'))

        # ============================================
        # 2. CATEGORIAS (asegurar 15)
        # ============================================
        cats = ['Laptop', 'Desktop', 'Monitor', 'Impresora', 'Servidor', 'Red', 'Periferico', 'Almacenamiento', 'UPS', 'General', 'Tablet', 'Smartphone', 'Proyector', 'Escáner', 'Videoconferencia']
        for c in cats:
            Categoria.objects.get_or_create(nombre=c)
        self.stdout.write(self.style.SUCCESS(f'✅ {Categoria.objects.count()} categorias'))

        # ============================================
        # 3. EQUIPOS (19) - si no existen
        # ============================================
        equipos_data = [
            ('Laptop HP ProBook 450', 'HP', 'ProBook 450 G8', 'HP001-MX', 'Equipo principal de desarrollo', 'disponible', 'Laptop', 'Oficina Principal'),
            ('Impresora HP LaserJet', 'HP', 'LaserJet Pro M404', 'HP002-MX', 'Impresora oficina principal', 'disponible', 'Impresora', 'Oficina Principal'),
            ('Tablet iPad Air', 'Apple', 'iPad Air 5', 'APL001', 'Tablet para presentaciones', 'disponible', 'Tablet', 'Sala de Juntas'),
            ('Desktop Dell OptiPlex', 'Dell', 'OptiPlex 7090', 'DELL001', 'Estacion de trabajo fija', 'disponible', 'Desktop', 'Area de Desarrollo'),
            ('Laptop Lenovo ThinkPad', 'Lenovo', 'ThinkPad T14', 'LEN001', 'Equipo de ventas', 'asignado', 'Laptop', 'Oficina Principal'),
            ('Monitor Samsung 27', 'Samsung', '27 pulgadas FHD', 'SAM001', 'Monitor secundario', 'disponible', 'Monitor', 'Area de Desarrollo'),
            ('Monitor LG 24', 'LG', '24MK430H', 'LG001', 'Monitor recepcion', 'disponible', 'Monitor', 'Recepcion'),
            ('Laptop Dell Latitude', 'Dell', 'Latitude 5520', 'DELL002', 'Equipo contabilidad', 'asignado', 'Laptop', 'Area Contable'),
            ('Tablet Samsung Galaxy', 'Samsung', 'Galaxy Tab A8', 'SNTAB001', 'Tablet para trabajo de campo', 'asignado', 'Tablet', 'Oficina Principal'),
            ('Impresora Brother', 'Brother', 'HL-L5200DW', 'BRO001', 'Impresora bodega', 'disponible', 'Impresora', 'Bodega'),
            ('Router TP-Link', 'TP-Link', 'Archer C6', 'TPL001', 'Router principal', 'disponible', 'Red', 'Sala de Servidores'),
            ('Disco Duro Seagate', 'Seagate', 'Expansion 2TB', 'SEA001', 'Backup de archivos', 'disponible', 'Almacenamiento', 'Sala de Servidores'),
            ('Webcam Logitech', 'Logitech', 'C920', 'LOG001', 'Videoconferencias', 'disponible', 'Periferico', 'Sala de Juntas'),
            ('Teclado Keychron', 'Keychron', 'K2', 'KEY001', 'Teclado desarrollo', 'disponible', 'Periferico', 'Area de Desarrollo'),
            ('Mouse Logitech MX', 'Logitech', 'MX Master 3', 'LOG002', 'Mouse ergonomico', 'disponible', 'Periferico', 'Area de Desarrollo'),
            ('Monitor Dell 24', 'Dell', 'P2419H', 'DELL003', 'Monitor extra', 'disponible', 'Monitor', 'Area Contable'),
            ('Laptop HP ProBook 440', 'HP', 'ProBook 440 G8', 'HP003-MX', 'Equipo respaldo', 'disponible', 'Laptop', 'Bodega'),
            ('Laptop Dell Latitude 54', 'Dell', 'Latitude 5420', 'DELL004', 'Equipo nuevo', 'disponible', 'Laptop', 'Oficina Principal'),
            ('Desktop Dell 3080', 'Dell', 'OptiPlex 3080', 'DELL005', 'PC recepcion', 'disponible', 'Desktop', 'Recepcion'),
        ]
        for nombre, marca, modelo, serial, desc, estado, cat_nombre, ubi_nombre in equipos_data:
            cat = Categoria.objects.filter(nombre=cat_nombre).first()
            ubi = Ubicacion.objects.filter(nombre=ubi_nombre).first()
            eq, created = Equipo.objects.get_or_create(serial=serial, defaults={
                'nombre': nombre, 'marca': marca, 'modelo': modelo,
                'descripcion': desc, 'estado': estado,
                'categoria': cat, 'ubicacion': ubi
            })
            if created:
                try:
                    eq._generar_qr()
                    eq.save(update_fields=['qr_code'])
                except Exception:
                    pass
        self.stdout.write(self.style.SUCCESS(f'✅ {Equipo.objects.count()} equipos'))

        # ============================================
        # 4. CLIENTES (5)
        # ============================================
        clientes_data = [
            ('Juan Perez', '1234567890101', '5555-1111', 'juan.perez@empresa.com'),
            ('Maria Garcia', '9876543210202', '5555-2222', 'maria.garcia@empresa.com'),
            ('Carlos Lopez', '4567891230303', '5555-3333', 'carlos.lopez@empresa.com'),
            ('Ana Martinez', '7891234560404', '5555-4444', 'ana.martinez@empresa.com'),
            ('Luis Torres', '3216549870505', '5555-5555', 'luis.torres@empresa.com'),
        ]
        for n, d, t, e in clientes_data:
            Cliente.objects.get_or_create(dpi=d, defaults={'nombre': n, 'telefono': t, 'email': e})
        self.stdout.write(self.style.SUCCESS(f'✅ {Cliente.objects.count()} clientes'))

        # ============================================
        # 5. ASIGNACIONES (5)
        # ============================================
        asigs = [
            ('LEN001', '1234567890101', 'Asignado a vendedor para trabajo de campo'),
            ('DELL002', '9876543210202', 'Equipo para contabilidad y finanzas'),
            ('SNTAB001', '4567891230303', 'Tablet para inspecciones externas'),
            ('DELL004', '7891234560404', 'Nuevo equipo para marketing'),
            ('HP001-MX', '3216549870505', 'Equipo principal de desarrollo'),
        ]
        for serial, dpi, obs in asigs:
            eq = Equipo.objects.filter(serial=serial).first()
            cl = Cliente.objects.filter(dpi=dpi).first()
            if eq and cl:
                Asignacion.objects.get_or_create(equipo=eq, defaults={'cliente': cl, 'observaciones': obs, 'activa': True})
        self.stdout.write(self.style.SUCCESS(f'✅ {Asignacion.objects.count()} asignaciones'))

        # ============================================
        # 6. ACCESORIOS (8 con stock critico)
        # ============================================
        accs_data = [
            ('Hub USB-C', 1, 3, 'Adaptador USB-C multi-puerto'),
            ('Teclado externo', 2, 2, 'Teclado inalambrico compacto'),
            ('Funda protectora', 3, 5, 'Funda para tablet 10 pulgadas'),
            ('Mouse inalambrico', 4, 3, 'Mouse optico inalambrico'),
            ('Cable HDMI', 5, 5, 'Cable HDMI 2.0 de 2 metros'),
            ('Cargador universal', 2, 4, 'Cargador USB-C 65W'),
            ('Audifonos con microfono', 3, 3, 'Audifonos USB para videollamadas'),
            ('Webcam HD externa', 1, 2, 'Webcam 1080p con microfono integrado'),
        ]
        for n, c, m, d in accs_data:
            Accesorio.objects.get_or_create(nombre=n, defaults={'cantidad': c, 'stock_minimo': m, 'descripcion': d})
        self.stdout.write(self.style.SUCCESS(f'✅ {Accesorio.objects.count()} accesorios'))

        # ============================================
        # 7. LICENCIAS DE SOFTWARE (6)
        # ============================================
        hoy = timezone.now().date()
        lic_data = [
            ('HP001-MX', 'office', 'Microsoft Office 365 Business', 'XXXXX-XXXXX-XXXXX-12345', hoy - relativedelta(months=6), hoy + relativedelta(days=30), 2500),
            ('HP001-MX', 'antivirus', 'Norton 360 Deluxe', 'YYYYY-YYYYY-YYYYY-67890', hoy - relativedelta(months=2), hoy + relativedelta(days=5), 800),
            ('DELL001', 'office', 'Microsoft Office 365 Business', 'ZZZZZ-ZZZZZ-ZZZZZ-11111', hoy - relativedelta(months=8), hoy + relativedelta(days=45), 2500),
            ('LEN001', 'sistema', 'Windows 11 Pro', 'WWWWW-WWWWW-WWWWW-22222', hoy - relativedelta(months=10), hoy + relativedelta(months=14), 1800),
            ('APL001', 'disenio', 'Adobe Creative Cloud', 'AAAAA-AAAAA-AAAAA-33333', hoy - relativedelta(months=4), hoy + relativedelta(days=60), 3200),
            ('DELL002', 'office', 'Microsoft Office 365 Business', 'BBBBB-BBBBB-BBBBB-44444', hoy - relativedelta(months=5), hoy + relativedelta(days=15), 2500),
        ]
        for serial, tipo, nombre, clave, ini, venc, costo in lic_data:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                SoftwareLicencia.objects.get_or_create(equipo=eq, nombre=nombre, defaults={
                    'tipo': tipo, 'clave_licencia': clave, 'fecha_inicio': ini,
                    'fecha_vencimiento': venc, 'costo': costo, 'activa': True
                })
        self.stdout.write(self.style.SUCCESS(f'✅ {SoftwareLicencia.objects.count()} licencias'))

        # ============================================
        # 8. MANTENIMIENTOS PREVENTIVOS (5)
        # ============================================
        mants_data = [
            ('HP001-MX', 'Limpieza interna y cambio de pasta termica', 'Desmontar laptop, limpiar ventiladores, aplicar pasta termica nueva', 'trimestral', hoy + relativedelta(months=3)),
            ('HP002-MX', 'Limpieza de cabezales y calibracion', 'Ejecutar ciclo de limpieza de cabezales, verificar niveles de tinta', 'mensual', hoy + relativedelta(months=1)),
            ('LG001', 'Revision de cables y conectores', 'Verificar integridad de cable HDMI, limpiar puertos y ajustar base', 'semestral', hoy + relativedelta(months=6)),
            ('DELL001', 'Actualizacion de sistema y antivirus', 'Instalar parches de seguridad, actualizar definiciones de virus', 'trimestral', hoy + relativedelta(months=2)),
            ('SAM001', 'Revision de pixeles y ajuste de color', 'Verificar pixeles muertos, calibrar perfil de color', 'anual', hoy + relativedelta(months=8)),
        ]
        for serial, titulo, desc, freq, prox in mants_data:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                MantenimientoPreventivo.objects.get_or_create(equipo=eq, titulo=titulo, defaults={
                    'descripcion': desc, 'frecuencia': freq, 'proxima_fecha': prox,
                    'tecnico': 'Luis Torres', 'completado': False
                })
        self.stdout.write(self.style.SUCCESS(f'✅ {MantenimientoPreventivo.objects.count()} mantenimientos'))

        # ============================================
        # 9. CAMBIOS Y REPARACIONES (4)
        # ============================================
        reps_data = [
            ('LEN001', 'Cambio de pantalla', 'Pantalla rota por caida, se reemplazo por nueva', 3500, 'reparacion'),
            ('HP002-MX', 'Cambio de toner', 'Toner agotado, se instalo cartucho nuevo', 850, 'cambio'),
            ('LG001', 'Reparacion de base', 'Base del monitor floja, se ajustaron tornillos y se reforzo', 400, 'reparacion'),
            ('DELL002', 'Cambio de bateria', 'Bateria no cargaba, se reemplazo por original', 1200, 'cambio'),
        ]
        for serial, tipo_falla, desc, costo, tipo_servicio in reps_data:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                CambioReparacion.objects.get_or_create(equipo=eq, tipo_falla=tipo_falla, defaults={
                    'descripcion': desc, 'costo': costo, 'tipo_servicio': tipo_servicio,
                    'fecha': hoy - relativedelta(days=15)
                })
        self.stdout.write(self.style.SUCCESS(f'✅ {CambioReparacion.objects.count()} cambios/reparaciones'))

        # ============================================
        # 10. HOJAS DE RESPONSABILIDAD (3)
        # ============================================
        hojas_data = [
            ('1234567890101', 'LEN001', 'El abajo firmante se hace responsable del equipo descrito en esta hoja. Se compromete a devolverlo en las mismas condiciones en que fue recibido. En caso de dano o perdida, cubrira el costo de reparacion o reposicion.'),
            ('9876543210202', 'DELL002', 'El abajo firmante se hace responsable del equipo descrito en esta hoja. Se compromete a devolverlo en las mismas condiciones en que fue recibido. En caso de dano o perdida, cubrira el costo de reparacion o reposicion.'),
            ('4567891230303', 'SNTAB001', 'El abajo firmante se hace responsable del equipo descrito en esta hoja. Se compromete a devolverlo en las mismas condiciones en que fue recibido. En caso de dano o perdida, cubrira el costo de reparacion o reposicion.'),
        ]
        for dpi, serial, cond in hojas_data:
            cl = Cliente.objects.filter(dpi=dpi).first()
            asig = Asignacion.objects.filter(equipo__serial=serial).first()
            if cl and asig:
                HojaResponsabilidad.objects.get_or_create(asignacion=asig, defaults={
                    'condiciones': cond, 'firmado': True,
                    'fecha_firma': hoy - relativedelta(days=10)
                })
        self.stdout.write(self.style.SUCCESS(f'✅ {HojaResponsabilidad.objects.count()} hojas de responsabilidad'))

        # ============================================
        # 11. NOTIFICACIONES (5)
        # ============================================
        notifs_data = [
            ('Bienvenido al sistema', 'Se ha configurado correctamente el inventario de equipos.', 'general'),
            ('Nuevo equipo registrado', 'Se han agregado 19 equipos al sistema.', 'general'),
            ('Revision pendiente', 'El equipo HP001-MX tiene mantenimiento programado.', 'mantenimiento'),
            ('Stock bajo', 'El accesorio Hub USB-C tiene stock critico.', 'stock'),
            ('Licencia por vencer', 'La licencia de Norton 360 Deluxe vence en 5 dias.', 'licencia'),
        ]
        for titulo, mensaje, tipo in notifs_data:
            Notificacion.objects.get_or_create(titulo=titulo, defaults={'mensaje': mensaje, 'tipo': tipo, 'leida': False})
        self.stdout.write(self.style.SUCCESS(f'✅ {Notificacion.objects.count()} notificaciones'))

        # ============================================
        # 12. EVIDENCIAS (3)
        # ============================================
        evids_data = [
            ('LEN001', 'Foto del estado inicial', 'Equipo recibido en buenas condiciones fisicas'),
            ('HP002-MX', 'Reporte de mantenimiento', 'Se realizo limpieza de cabezales correctamente'),
            ('DELL001', 'Entrega de equipo', 'Equipo entregado al usuario con todos sus accesorios'),
        ]
        for serial, titulo, desc in evids_data:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                Evidencia.objects.get_or_create(equipo=eq, titulo=titulo, defaults={'descripcion': desc})
        self.stdout.write(self.style.SUCCESS(f'✅ {Evidencia.objects.count()} evidencias'))

        # ============================================
        # 13. ALERTAS (5)
        # ============================================
        alertas_data = [
            ('stock', 'Stock bajo: Hub USB-C', 'El accesorio Hub USB-C tiene solo 1 unidad (minimo 3).'),
            ('stock', 'Stock bajo: Teclado externo', 'El accesorio Teclado externo tiene solo 2 unidades (minimo 2).'),
            ('licencia', 'Licencia por vencer: Norton 360 Deluxe', 'La licencia vence en 5 dias en Laptop HP ProBook.'),
            ('licencia', 'Licencia por vencer: Microsoft Office 365', 'La licencia vence en 30 dias en Laptop HP ProBook.'),
            ('general', 'Fin de soporte Windows 10', 'Se recomienda actualizar equipos a Windows 11.'),
        ]
        for tipo, titulo, desc in alertas_data:
            Alerta.objects.get_or_create(titulo=titulo, defaults={'tipo': tipo, 'descripcion': desc, 'resuelta': False})
        self.stdout.write(self.style.SUCCESS(f'✅ {Alerta.objects.count()} alertas'))

        # ============================================
        # RESUMEN FINAL
        # ============================================
        self.stdout.write(self.style.NOTICE('\n📊 RESUMEN DE DATOS EN LA NUBE:'))
        self.stdout.write(self.style.NOTICE(f'  Ubicaciones: {Ubicacion.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Categorias: {Categoria.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Equipos: {Equipo.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Clientes: {Cliente.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Asignaciones: {Asignacion.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Accesorios: {Accesorio.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Licencias: {SoftwareLicencia.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Mantenimientos: {MantenimientoPreventivo.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Cambios/Reparaciones: {CambioReparacion.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Hojas de Responsabilidad: {HojaResponsabilidad.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Notificaciones: {Notificacion.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Evidencias: {Evidencia.objects.count()}'))
        self.stdout.write(self.style.NOTICE(f'  Alertas: {Alerta.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡TODO LISTO! Datos permanentes creados en la nube.'))
