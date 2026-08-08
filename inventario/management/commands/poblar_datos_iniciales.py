from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from inventario.models import (
    Equipo, Categoria, Ubicacion, Cliente, Asignacion,
    SoftwareLicencia, MantenimientoPreventivo, Accesorio
)

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('🚀 Iniciando carga de datos...'))

        # CATEGORIAS (asegurar que existan)
        cats = ['Laptop','Desktop','Monitor','Impresora','Servidor','Red','Periferico','Almacenamiento','UPS','General','Tablet','Smartphone','Proyector','Escáner','Videoconferencia']
        for c in cats:
            Categoria.objects.get_or_create(nombre=c)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(cats)} categorías'))

        # UBICACIONES
        ubis = [('Oficina Principal','Oficina central','Admin'),('Sala de Servidores','Servidores','Admin Sistemas'),('Bodega','Almacén','Almacén'),('Recepción','Atención','Recepcionista'),('Sala de Juntas','Reuniones','Coordinador'),('Área de Desarrollo','Programación','Líder Dev'),('Área Contable','Contabilidad','Jefe Contable'),('Sala de Capacitación','Capacitación','Coordinador'),('Home Office','Remoto','N/A')]
        for n,d,r in ubis:
            Ubicacion.objects.get_or_create(nombre=n, defaults={'descripcion':d,'responsable':r,'activa':True})
        self.stdout.write(self.style.SUCCESS(f'✅ {len(ubis)} ubicaciones'))

        # EQUIPOS (19)
        equipos_data = [
            ('Laptop HP ProBook 450','HP','ProBook 450 G8','HP001-MX','Equipo desarrollo','disponible','Laptop','Oficina Principal'),
            ('Impresora HP LaserJet','HP','LaserJet Pro','HP002-MX','Impresora oficina','disponible','Impresora','Oficina Principal'),
            ('Tablet iPad Air','Apple','iPad Air 5','APL001','Presentaciones','disponible','Tablet','Sala de Juntas'),
            ('Desktop Dell OptiPlex','Dell','OptiPlex 7090','DELL001','Estación trabajo','disponible','Desktop','Área de Desarrollo'),
            ('Laptop Lenovo ThinkPad','Lenovo','ThinkPad T14','LEN001','Ventas','asignado','Laptop','Oficina Principal'),
            ('Monitor Samsung 27','Samsung','27 FHD','SAM001','Monitor secundario','disponible','Monitor','Área de Desarrollo'),
            ('Monitor LG 24','LG','24MK430H','LG001','Recepción','disponible','Monitor','Recepción'),
            ('Laptop Dell Latitude','Dell','Latitude 5520','DELL002','Contabilidad','asignado','Laptop','Área Contable'),
            ('Tablet Samsung Galaxy','Samsung','Galaxy Tab A8','SNTAB001','Campo','asignado','Tablet','Oficina Principal'),
            ('Impresora Brother','Brother','HL-L5200DW','BRO001','Bodega','disponible','Impresora','Bodega'),
            ('Router TP-Link','TP-Link','Archer C6','TPL001','Router principal','disponible','Red','Sala de Servidores'),
            ('Disco Duro Seagate','Seagate','Expansion 2TB','SEA001','Backup','disponible','Almacenamiento','Sala de Servidores'),
            ('Webcam Logitech','Logitech','C920','LOG001','Video llamadas','disponible','Periferico','Sala de Juntas'),
            ('Teclado Keychron','Keychron','K2','KEY001','Desarrollo','disponible','Periferico','Área de Desarrollo'),
            ('Mouse Logitech MX','Logitech','MX Master 3','LOG002','Ergonómico','disponible','Periferico','Área de Desarrollo'),
            ('Monitor Dell 24','Dell','P2419H','DELL003','Extra','disponible','Monitor','Área Contable'),
            ('Laptop HP ProBook 440','HP','ProBook 440 G8','HP003-MX','Respaldo','disponible','Laptop','Bodega'),
            ('Laptop Dell Latitude 54','Dell','Latitude 5420','DELL004','Nuevo','disponible','Laptop','Oficina Principal'),
            ('Desktop Dell 3080','Dell','OptiPlex 3080','DELL005','Recepción','disponible','Desktop','Recepción'),
        ]
        creados = 0
        for nombre,marca,modelo,serial,desc,estado,cat_nombre,ubi_nombre in equipos_data:
            cat = Categoria.objects.filter(nombre=cat_nombre).first()
            ubi = Ubicacion.objects.filter(nombre=ubi_nombre).first()
            eq, created = Equipo.objects.get_or_create(serial=serial, defaults={
                'nombre':nombre,'marca':marca,'modelo':modelo,'descripcion':desc,'estado':estado,'categoria':cat,'ubicacion':ubi
            })
            if created:
                try:
                    eq._generar_qr()
                    eq.save(update_fields=['qr_code'])
                except Exception:
                    pass
                creados += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {creados} equipos creados'))

        # CLIENTES (3)
        clientes = [('Juan Pérez','1234567890101','5555-1111','juan@empresa.com'),('María García','9876543210202','5555-2222','maria@empresa.com'),('Carlos López','4567891230303','5555-3333','carlos@empresa.com')]
        for n,d,t,e in clientes:
            Cliente.objects.get_or_create(dpi=d, defaults={'nombre':n,'telefono':t,'email':e})
        self.stdout.write(self.style.SUCCESS(f'✅ {len(clientes)} clientes'))

        # ASIGNACIONES
        asigs = [('LEN001','1234567890101'),('DELL002','9876543210202'),('SNTAB001','4567891230303')]
        for serial,dpi in asigs:
            eq = Equipo.objects.filter(serial=serial).first()
            cl = Cliente.objects.filter(dpi=dpi).first()
            if eq and cl:
                Asignacion.objects.get_or_create(equipo=eq, defaults={'cliente':cl,'observaciones':'Asignación inicial'})
        self.stdout.write(self.style.SUCCESS('✅ 3 asignaciones'))

        # LICENCIAS
        hoy = timezone.now().date()
        licencias = [
            ('HP001-MX','office','Microsoft Office 365','XXXXX-XXXXX-12345',hoy-relativedelta(months=6),hoy+relativedelta(days=30),2500),
            ('HP001-MX','antivirus','Norton 360 Deluxe','YYYYY-YYYYY-67890',hoy-relativedelta(months=2),hoy+relativedelta(days=5),800),
            ('DELL001','office','Microsoft Office 365','ZZZZZ-ZZZZZ-11111',hoy-relativedelta(months=8),hoy+relativedelta(days=45),2500),
        ]
        for serial,tipo,nombre,clave,ini,venc,costo in licencias:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                SoftwareLicencia.objects.get_or_create(equipo=eq, nombre=nombre, defaults={'tipo':tipo,'clave_licencia':clave,'fecha_inicio':ini,'fecha_vencimiento':venc,'costo':costo,'activa':True})
        self.stdout.write(self.style.SUCCESS('✅ 3 licencias'))

        # MANTENIMIENTOS
        mants = [
            ('HP001-MX','Limpieza interna','Cambio pasta térmica','trimestral',hoy+relativedelta(months=3)),
            ('HP002-MX','Limpieza cabezales','Calibración color','mensual',hoy+relativedelta(months=1)),
            ('LG001','Revisión cables','Verificar HDMI','semestral',hoy+relativedelta(months=6)),
        ]
        for serial,titulo,desc,freq,prox in mants:
            eq = Equipo.objects.filter(serial=serial).first()
            if eq:
                MantenimientoPreventivo.objects.get_or_create(equipo=eq, titulo=titulo, defaults={'descripcion':desc,'frecuencia':freq,'proxima_fecha':prox,'tecnico':'Luis Torres'})
        self.stdout.write(self.style.SUCCESS('✅ 3 mantenimientos'))

        # ACCESORIOS
        accs = [('Hub USB-C',1,3,'Oficina Principal'),('Teclado externo',2,2,'Oficina Principal'),('Funda protectora',3,5,'Bodega'),('Mouse inalámbrico',4,3,'Oficina Principal'),('Cable HDMI',5,5,'Sala de Juntas')]
        for n,s,m,u in accs:
            ub = Ubicacion.objects.filter(nombre=u).first()
            Accesorio.objects.get_or_create(nombre=n, defaults={'stock_actual':s,'stock_minimo':m,'ubicacion':ub})
        self.stdout.write(self.style.SUCCESS('✅ 5 accesorios'))

        self.stdout.write(self.style.NOTICE('\n🎉 ¡Listo! Todo poblado en la nube.'))
