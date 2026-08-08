import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.db import models
from inventario.models import (
    Categoria, Ubicacion, Equipo, Cliente, Accesorio,
    Asignacion, CambioReparacion, HojaResponsabilidad,
    SoftwareLicencia, MantenimientoPreventivo, Alerta, Evidencia
)

print("🌱 Iniciando carga de datos de prueba...")

categorias = list(Categoria.objects.all())
ubicaciones = list(Ubicacion.objects.filter(activa=True))

if not categorias:
    print("❌ No hay categorias. Ejecuta primero el seed de categorias.")
    exit(1)
if not ubicaciones:
    print("❌ No hay ubicaciones. Ejecuta primero el seed de ubicaciones.")
    exit(1)

MARCAS_MODELOS = {
    'Dell': ['Latitude 5520', 'OptiPlex 7090', 'PowerEdge T340', 'P2419H', 'S2721D'],
    'HP': ['EliteBook 840 G8', 'ProDesk 600 G6', 'LaserJet Pro M404', 'Pavilion 27', 'ZBook Fury'],
    'Lenovo': ['ThinkPad T14', 'ThinkCentre M90q', 'IdeaPad 5', 'ThinkVision T24', 'Legion 5'],
    'Asus': ['VivoBook 15', 'ExpertCenter D7', 'ProArt PA278QV', 'ZenBook 14', 'TUF Gaming'],
    'Acer': ['Aspire 5', 'Veriton X4660G', 'Nitro 5', 'CB242Y', 'TravelMate P2'],
    'Apple': ['MacBook Pro 14', 'MacBook Air M2', 'iMac 24', 'Mac Mini M2', 'Studio Display'],
    'LG': ['24MK430H', '27UP600', '34WN650', '24MP400', '32QN600'],
    'Samsung': ['Galaxy Book3', 'Odyssey G5', 'T35F', 'S24A310', 'Smart Monitor M7'],
    'Cisco': ['Catalyst 2960', 'Aironet 1852', 'RV345', 'SG350-28', 'Meraki MX68'],
    'Ubiquiti': ['UniFi AP AC Pro', 'UniFi Switch 24', 'EdgeRouter X', 'UniFi 6 LR', 'NanoBeam'],
    'Eaton': ['5E 850VA', '5S 1500VA', '9SX 2000VA', 'Ellipse ECO 650', '3S 550VA'],
    'APC': ['Back-UPS 650VA', 'Smart-UPS 1500VA', 'Back-UPS Pro 900', 'Easy UPS 700VA', 'Smart-UPS 2200VA'],
}

NOMBRES_GUATEMALTECOS = [
    'Juan Perez', 'Maria Garcia', 'Carlos Mendez', 'Ana Lopez', 'Luis Torres',
    'Diana Herrera', 'Pedro Ruiz', 'Sandra Morales', 'Fernando Paz', 'Roberto Diaz',
    'Miguel Angel', 'Jose Martinez', 'Laura Castillo', 'Andres Estrada', 'Carmen Reyes',
    'Diego Alvarado', 'Patricia Fuentes', 'Ricardo Ordonez', 'Gabriela Vargas', 'Hector Aguilar',
    'Alejandra Mora', 'Francisco Rivas', 'Daniela Cruz', 'Sergio Palacios', 'Monica Soto',
    'Eduardo Lemus', 'Natalia Arriaza', 'Julio Cesar', 'Stephanie Castaneda', 'Marco Tulio',
    'Brenda Recinos', 'Walter Guerra', 'Katherine Recinos', 'Omar Fuentes', 'Jessica Morales',
    'Raul Mejia', 'Paola Gonzalez', 'Edwin Escobar', 'Melissa Pineda', 'Kevin Argueta',
]

DEPARTAMENTOS = [
    'Guatemala', 'Mixco', 'Villa Nueva', 'Quetzaltenango', 'Escuintla',
    'San Miguel Petapa', 'Villa Canales', 'San Jose Pinula', 'Santa Catarina Pinula', 'Amatitlan',
    'Fraijanes', 'San Lucas Sacatepequez', 'Antigua Guatemala', 'Chimaltenango', 'Huehuetenango',
]

ACCESORIOS_DATA = [
    ('Mouse Logitech', 'Mouse optico USB inalambrico', 45, 10),
    ('Teclado HP', 'Teclado USB estandar español', 38, 10),
    ('Webcam Logitech C920', 'Camara HD 1080p para videollamadas', 22, 5),
    ('Disco Duro Externo 1TB', 'WD Elements USB 3.0', 18, 5),
    ('Memoria USB 32GB', 'Kingston DataTraveler', 60, 15),
    ('Cable HDMI 2m', 'Cable HDMI 2.0 alta velocidad', 80, 20),
    ('Base Laptop', 'Base refrigerante ajustable', 25, 8),
    ('Audifonos JBL', 'Audifonos con microfono para llamadas', 30, 10),
    ('Hub USB 4 puertos', 'Hub USB 3.0 con alimentacion', 35, 10),
    ('Mochila Laptop', 'Mochila antirrobo para laptop 15.6"', 20, 5),
    ('Protector Pantalla', 'Filtro de privacidad 24 pulgadas', 15, 5),
    ('Soporte Monitor', 'Soporte ajustable para monitor doble', 12, 3),
    ('Cable Ethernet 5m', 'Cable Cat6 para red', 50, 15),
    ('Adaptador USB-C', 'Adaptador multipuerto USB-C HDMI', 20, 5),
    ('Bateria Portatil', 'Power bank 20000mAh', 15, 5),
]

print("\n📦 Creando accesorios...")
for nombre, desc, cantidad, minimo in ACCESORIOS_DATA:
    obj, created = Accesorio.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': desc, 'cantidad': cantidad, 'stock_minimo': minimo}
    )
    if created:
        print(f"  + {nombre} ({cantidad} unidades)")

accesorios = list(Accesorio.objects.all())

print("\n👤 Creando clientes...")
clientes_creados = []
for i, nombre in enumerate(NOMBRES_GUATEMALTECOS[:20]):
    dpi = f"{random.randint(1000000000000, 9999999999999)}"
    telefono = f"{random.choice(['502', '501', '502'])} {random.randint(40000000, 59999999)}"
    email = f"{nombre.lower().replace(' ', '.')}@empresa.local"
    direccion = f"{random.randint(1, 50)} Avenida, Zona {random.randint(1, 18)}, {random.choice(DEPARTAMENTOS)}"
    obj, created = Cliente.objects.get_or_create(
        dpi=dpi,
        defaults={'nombre': nombre, 'telefono': telefono, 'email': email, 'direccion': direccion}
    )
    if created:
        clientes_creados.append(obj)
        print(f"  + {nombre}")

if not clientes_creados:
    clientes_creados = list(Cliente.objects.all()[:20])

print("\n💻 Creando equipos...")
equipos_creados = []

for i in range(30):
    marca = random.choice(list(MARCAS_MODELOS.keys()))
    modelo = random.choice(MARCAS_MODELOS[marca])
    serial = f"SN{marca[:3].upper()}{random.randint(100000, 999999)}{i:03d}"
    while Equipo.objects.filter(serial=serial).exists():
        serial = f"SN{marca[:3].upper()}{random.randint(100000, 999999)}{i:03d}"
    
    categoria = random.choice(categorias)
    ubicacion = random.choice(ubicaciones)
    
    nombres_equipo = {
        'Laptop': f"Laptop {marca} {modelo}",
        'Desktop': f"PC {marca} {modelo}",
        'Monitor': f"Monitor {marca} {modelo}",
        'Impresora': f"Impresora {marca} {modelo}",
        'Servidor': f"Servidor {marca} {modelo}",
        'Tablet': f"Tablet {marca} {modelo}",
        'Celular': f"Celular {marca} {modelo}",
        'Periferico': f"{marca} {modelo}",
        'Red': f"Equipo de Red {marca} {modelo}",
        'Almacenamiento': f"Almacenamiento {marca} {modelo}",
        'UPS': f"UPS {marca} {modelo}",
        'Otro': f"Equipo {marca} {modelo}",
    }
    
    nombre = nombres_equipo.get(categoria.nombre, f"Equipo {marca} {modelo}")
    descripcion = f"Equipo {marca} modelo {modelo} adquirido para uso corporativo."
    fecha_garantia = date.today() + timedelta(days=random.randint(-180, 730))
    
    equipo = Equipo.objects.create(
        nombre=nombre,
        categoria=categoria,
        marca=marca,
        modelo=modelo,
        serial=serial,
        descripcion=descripcion,
        estado='disponible',
        ubicacion=ubicacion,
        fecha_fin_garantia=fecha_garantia,
    )
    equipos_creados.append(equipo)
    print(f"  + {nombre} ({serial}) - {categoria.nombre}")

print("\n📋 Creando asignaciones...")
asignaciones_creadas = []

for equipo in random.sample(equipos_creados, min(15, len(equipos_creados))):
    cliente = random.choice(clientes_creados)
    ubic = random.choice(ubicaciones)
    dias_atras = random.randint(1, 730)
    fecha_asig = timezone.now() - timedelta(days=dias_atras)
    
    asignacion = Asignacion.objects.create(
        equipo=equipo,
        cliente=cliente,
        ubicacion=ubic,
        fecha_asignacion=fecha_asig,
        activa=True,
        observaciones=f"Asignado para uso diario en {ubic.nombre}."
    )
    accs = random.sample(accesorios, random.randint(1, 3))
    asignacion.accesorios_entregados.set(accs)
    
    # CORRECCION: Usar transicion FSM
    equipo.asignar()
    equipo.save()
    
    asignaciones_creadas.append(asignacion)
    print(f"  + {equipo.nombre} -> {cliente.nombre}")

print("\n📝 Creando hojas de responsabilidad...")
for asig in asignaciones_creadas:
    HojaResponsabilidad.objects.get_or_create(
        asignacion=asig,
        defaults={
            'condiciones': "El abajo firmante se hace responsable del equipo descrito en esta hoja. "
                           "Se compromete a devolverlo en las mismas condiciones en que fue recibido. "
                           "En caso de dano o perdida, cubrira el costo de reparacion o reposicion."
        }
    )
print(f"  + {len(asignaciones_creadas)} hojas creadas")

print("\n🔧 Creando reparaciones...")
tipos_reparacion = ['reparacion', 'cambio_pieza', 'actualizacion', 'mantenimiento']
descripciones = [
    "Cambio de pantalla por fractura en display.",
    "Actualizacion de memoria RAM de 8GB a 16GB.",
    "Reemplazo de bateria por perdida de carga.",
    "Mantenimiento preventivo: limpieza interna y cambio de pasta termica.",
    "Reparacion de puerto USB danado.",
    "Cambio de disco duro HDD por SSD de 512GB.",
    "Actualizacion de sistema operativo a version mas reciente.",
    "Reparacion de teclado por derrame de liquido.",
    "Cambio de fuente de poder por falla electrica.",
    "Mantenimiento de impresora: cambio de rodillos y limpieza de cabezal.",
]
tecnicos = ['Luis Torres', 'Sandra Morales', 'Fernando Paz', 'Carlos Mendez', 'Ana Lopez']

for i in range(15):
    equipo = random.choice(equipos_creados)
    tipo = random.choice(tipos_reparacion)
    desc = random.choice(descripciones)
    tecnico = random.choice(tecnicos)
    costo = Decimal(random.randint(150, 5000))
    fecha_rep = timezone.now() - timedelta(days=random.randint(1, 365))
    
    CambioReparacion.objects.create(
        equipo=equipo,
        tipo=tipo,
        descripcion=desc,
        tecnico=tecnico,
        fecha=fecha_rep,
        costo=costo
    )
    print(f"  + {tipo} - {equipo.nombre[:30]}... (Q{costo})")

print("\n🔑 Creando licencias de software...")
licencias_data = [
    ('Windows 11 Pro', 'os', 365),
    ('Microsoft Office 365', 'office', 365),
    ('Kaspersky Endpoint Security', 'antivirus', 365),
    ('AutoCAD 2024', 'cad', 365),
    ('Adobe Creative Cloud', 'otro', 365),
    ('SQL Server 2022', 'db', 730),
    ('VMware Workstation', 'otro', 730),
    ('Norton Antivirus', 'antivirus', 365),
    ('Windows Server 2022', 'os', 730),
    ('Microsoft Project', 'office', 365),
]

for i in range(20):
    equipo = random.choice(equipos_creados)
    nombre, tipo, dias_duracion = random.choice(licencias_data)
    fecha_inicio = date.today() - timedelta(days=random.randint(0, 300))
    fecha_venc = fecha_inicio + timedelta(days=dias_duracion)
    clave = f"XXXXX-XXXXX-XXXXX-XXXXX-{random.randint(10000,99999)}"
    costo = Decimal(random.randint(500, 8000))
    
    SoftwareLicencia.objects.get_or_create(
        equipo=equipo,
        nombre=nombre,
        defaults={
            'tipo': tipo,
            'clave': clave,
            'fecha_inicio': fecha_inicio,
            'fecha_vencimiento': fecha_venc,
            'costo': costo,
            'activa': True
        }
    )
    print(f"  + {nombre} - {equipo.nombre[:25]}... (vence {fecha_venc})")

print("\n🔧 Creando mantenimientos preventivos...")
mantenimientos_data = [
    ("Limpieza interna y cambio de pasta termica", "trimestral"),
    ("Revision de bateria y calibracion", "semestral"),
    ("Actualizacion de firmware y drivers", "trimestral"),
    ("Limpieza de ventiladores y disipadores", "mensual"),
    ("Revision de cables y conectores", "semestral"),
    ("Escaneo de virus y optimizacion", "mensual"),
    ("Respaldo de datos y verificacion", "semanal"),
    ("Revision de rendimiento y temperatura", "mensual"),
    ("Limpieza de pantalla y teclado", "semanal"),
    ("Revision de garantia y estado fisico", "anual"),
]

for i in range(15):
    equipo = random.choice(equipos_creados)
    titulo, frecuencia = random.choice(mantenimientos_data)
    tecnico = random.choice(tecnicos)
    dias = random.randint(-90, 30)
    ultima = date.today() + timedelta(days=dias)
    
    MantenimientoPreventivo.objects.create(
        equipo=equipo,
        titulo=titulo,
        descripcion=f"{titulo} programado para el equipo {equipo.nombre}.",
        frecuencia=frecuencia,
        ultima_fecha=ultima if dias <= 0 else None,
        tecnico=tecnico,
        completado=dias <= 0
    )
    print(f"  + {titulo[:40]}... - {equipo.nombre[:25]}... ({frecuencia})")

print("\n⚠️ Verificando alertas automaticas...")
hoy = date.today()

for eq in Equipo.objects.filter(fecha_fin_garantia__lte=hoy+timedelta(days=30), fecha_fin_garantia__gte=hoy)[:3]:
    Alerta.objects.get_or_create(
        tipo='garantia',
        equipo=eq,
        defaults={'titulo': f'Garantia por vencer: {eq}', 'mensaje': f'La garantia del equipo {eq} vence el {eq.fecha_fin_garantia}.'}
    )

for acc in Accesorio.objects.filter(cantidad__lte=models.F('stock_minimo'))[:3]:
    Alerta.objects.get_or_create(
        tipo='stock',
        accesorio=acc,
        defaults={'titulo': f'Stock bajo: {acc.nombre}', 'mensaje': f'El accesorio {acc.nombre} tiene {acc.cantidad} unidades (minimo {acc.stock_minimo}).'}
    )
print("  + Alertas de garantia y stock creadas")

print("\n📷 Creando evidencias...")
tipos_evidencia = ['asignacion', 'devolucion', 'reparacion', 'general']
for i in range(10):
    equipo = random.choice(equipos_creados)
    tipo = random.choice(tipos_evidencia)
    descs = {
        'asignacion': 'Foto de entrega del equipo al usuario.',
        'devolucion': 'Foto de recepcion del equipo devuelto.',
        'reparacion': 'Foto del estado del equipo antes de reparacion.',
        'general': 'Foto de inventario general del equipo.',
    }
    Evidencia.objects.create(
        equipo=equipo,
        tipo=tipo,
        descripcion=descs[tipo]
    )
    print(f"  + {tipo} - {equipo.nombre[:30]}...")

print("\n" + "="*50)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("="*50)
print(f"""
📊 Resumen:
   • {len(accesorios)} Accesorios
   • {len(clientes_creados)} Clientes
   • {len(equipos_creados)} Equipos
   • {len(asignaciones_creadas)} Asignaciones activas
   • 15 Reparaciones registradas
   • 20 Licencias de software
   • 15 Mantenimientos preventivos
   • 10 Evidencias
   • Alertas de garantia y stock generadas

🌐 URLs para probar:
   Dashboard:      http://127.0.0.1:8000/
   Metricas:       http://127.0.0.1:8000/metricas/
   Mantenimientos: http://127.0.0.1:8000/mantenimientos/
   Licencias:      http://127.0.0.1:8000/licencias/
   Reportes:       http://127.0.0.1:8000/reportes/equipos/
""")
