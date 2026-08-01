# 📘 Manual de Usuario — Sistema de Inventario de Equipos Tecnológicos

**Versión:** 2.0  
**Fecha:** Agosto 2026  
**Plataforma:** Web (Django + Render)  
**URL de acceso:** `https://inventario-equipos-hkmd.onrender.com`

---

## 📑 Índice

1. [Primeros pasos](#1-primeros-pasos)
2. [El Dashboard](#2-el-dashboard)
3. [Gestión de Equipos](#3-gestión-de-equipos)
4. [Asignaciones a Personal](#4-asignaciones-a-personal)
5. [Mantenimientos](#5-mantenimientos)
6. [Licencias de Software](#6-licencias-de-software)
7. [Alertas del Sistema](#7-alertas-del-sistema)
8. [Reportes y Exportaciones](#8-reportes-y-exportaciones)
9. [Accesorios y Stock](#9-accesorios-y-stock)
10. [Evidencias Fotográficas](#10-evidencias-fotográficas)
11. [Escaneo de Códigos QR](#11-escaneo-de-códigos-qr)
12. [Métricas y Estadísticas](#12-métricas-y-estadísticas)
13. [Roles de Usuario](#13-roles-de-usuario)
14. [Flujos de trabajo recomendados](#14-flujos-de-trabajo-recomendados)
15. [Solución de problemas](#15-solución-de-problemas)

---

## 1. Primeros pasos

### 1.1 Requisitos
- Navegador web actualizado (Chrome, Firefox, Edge, Safari).
- Conexión a internet.
- Credenciales de acceso proporcionadas por el administrador.

### 1.2 Cómo ingresar
1. Abre tu navegador y escribe la URL del sistema.
2. Haz clic en **"Panel Admin"** o ve directamente a `/admin/`.
3. Ingresa tu **usuario** y **contraseña**.
4. Haz clic en **"Iniciar sesión"**.

> 🔒 **Seguridad:** No compartas tu contraseña. Si la olvidas, contacta al administrador.

### 1.3 Cierre de sesión
- Haz clic en tu nombre de usuario (esquina superior derecha).
- Selecciona **"Salir"** o **"Cerrar sesión"**.

---

## 2. El Dashboard

El Dashboard es la pantalla principal. Proporciona una vista rápida del estado completo del inventario.

### 2.1 KPIs principales (tarjetas superiores)

| Tarjeta | Color | Significado |
|---------|-------|-------------|
| **Total Equipos** | Azul | Cantidad total registrada. |
| **Disponibles** | Verde | Equipos listos para asignar. |
| **Asignados** | Celeste | Equipos entregados a personal. |
| **En Reparación** | Amarillo | Equipos con fallas o en taller. |
| **Dados de Baja** | Gris | Equipos retirados del inventario. |
| **Costo Reparaciones** | Negro | Dinero total gastado en reparaciones. |

### 2.2 Gráficas
- **Equipos por Estado:** Gráfico circular con la distribución visual.
- **Top Marcas:** Gráfico de barras con las marcas más frecuentes.
- **Equipos por Categoría:** Gráfico circular con laptops, monitores, servidores, etc.
- **Equipos por Ubicación:** Gráfico de barras mostrando dónde están físicamente.

### 2.3 Paneles de alertas

#### ⚠️ Alertas Pendientes
Lista de notificaciones que requieren atención:
- **Garantía por vencer:** El equipo perderá garantía pronto.
- **Mantenimiento preventivo:** Toca revisar el equipo.
- **Stock bajo:** Un accesorio está por agotarse.
- **Revisión pendiente:** Equipo asignado lleva más de 1 año sin revisión.

> ✅ Para marcar una alerta como leída, haz clic en el botón **"✓"** a la derecha.

#### 📦 Stock Crítico
Muestra accesorios cuya cantidad actual es igual o menor al mínimo permitido. Ejemplo: `Hub USB-C 1 / min 3` significa que solo queda 1 unidad y el mínimo es 3.

#### 🔑 Licencias por Vencer
Software (Windows, Office, antivirus) cuya licencia expira en los próximos 30 días.

#### 🔧 Mantenimientos Próximos
Lista de mantenimientos preventivos programados para esta semana.

#### 👤 Clientes con más Equipos
Ranking de quién tiene más equipos asignados actualmente.

#### 🔴 Equipos con más Fallas
Ranking de equipos que más veces han sido reparados.

---

## 3. Gestión de Equipos

### 3.1 Crear un nuevo equipo
1. Ve a **Panel Admin → Inventario → Equipos → Añadir**.
2. Completa los campos:
   - **Nombre:** Descripción clara (ej: "Laptop Dell Latitude 5520").
   - **Categoría:** Selecciona del listado (Laptop, Monitor, Servidor, etc.).
   - **Marca:** Ej: Dell, HP, Lenovo.
   - **Modelo:** Ej: Latitude 5520.
   - **Serial:** Número de serie único (obligatorio, no se puede repetir).
   - **Descripción:** Detalles adicionales.
   - **Ubicación:** Dónde se encuentra físicamente.
   - **Fecha fin de garantía:** Cuándo vence la garantía del fabricante.
   - **Foto:** Imagen del equipo (opcional).
3. Haz clic en **"Guardar"**.

> 📝 **Nota:** El sistema genera automáticamente un **UUID** y un **código QR** para el equipo al guardar.

### 3.2 Ver ficha de un equipo
1. En el listado de equipos, haz clic en el nombre del equipo.
2. Verás todos sus datos, historial de cambios, QR generado y estado actual.

### 3.3 Cambiar estado de un equipo (FSM)
El sistema usa un flujo de estados protegido. Desde el Admin, en la columna **"Acciones"** verás botones según el estado actual:

| Estado actual | Acciones disponibles |
|---------------|----------------------|
| **Disponible** | Asignar, Dar de Baja |
| **Asignado** | Reportar Fallo |
| **En Reparación** | Reparar, Dar de Baja |
| **Dado de Baja** | Ninguna (equipo retirado) |

> ⚠️ **Importante:** No puedes cambiar el estado manualmente escribiendo. Debes usar los botones de acción.

### 3.4 Editar o eliminar
- **Editar:** Abre el equipo, modifica los campos y guarda.
- **Eliminar:** En la lista, selecciona el equipo, elige **"Eliminar equipos seleccionados"** en el menú desplegable y confirma.

---

## 4. Asignaciones a Personal

### 4.1 Asignar un equipo a una persona
1. Asegúrate de que el equipo esté en estado **"Disponible"**.
2. Ve a **Panel Admin → Inventario → Asignaciones → Añadir**.
3. Selecciona:
   - **Equipo:** El que vas a entregar.
   - **Cliente:** La persona que recibirá el equipo.
   - **Ubicación física:** Dónde usará el equipo.
   - **Observaciones:** Condiciones especiales de entrega.
   - **Accesorios entregados:** Mouse, teclado, mochila, etc.
4. Guarda la asignación.

> ✅ El sistema cambiará automáticamente el estado del equipo a **"Asignado"**.

### 4.2 Generar Hoja de Responsabilidad
Cuando creas una asignación, el sistema genera automáticamente una **Hoja de Responsabilidad**. Es un documento legal que indica que la persona se hace responsable del equipo.

Para firmarla digitalmente:
1. Ve a la asignación y busca la sección **"Hoja de Responsabilidad"**.
2. Haz clic en **"Firmar digitalmente"**.
3. Dibuja tu firma en el canvas.
4. Guarda.

### 4.3 Devolver un equipo
1. Busca la asignación activa en **Panel Admin → Asignaciones**.
2. Abre la asignación.
3. El sistema marca la asignación como inactiva, registra la fecha de devolución y cambia el estado del equipo a **"Disponible"** automáticamente.

---

## 5. Mantenimientos

### 5.1 Mantenimiento Correctivo (Reparaciones)
Usa esto cuando un equipo se daña o necesita una reparación puntual.

1. Ve a **Panel Admin → Inventario → Cambios y Reparaciones → Añadir**.
2. Completa:
   - **Equipo:** El que se reparará.
   - **Tipo:** Reparación, Cambio de Pieza, Actualización o Mantenimiento.
   - **Descripción:** Qué le pasó al equipo y qué se hizo.
   - **Técnico:** Quién realizó la reparación.
   - **Costo:** Cuánto costó (en Quetzales).
3. Guarda.

> 💡 **Tip:** Si el costo es alto, el equipo aparecerá en el ranking de "Equipos con más Fallas".

### 5.2 Mantenimiento Preventivo
Programa revisiones periódicas para evitar fallas.

1. Ve a **Panel Admin → Inventario → Mantenimientos Preventivos → Añadir**.
2. Completa:
   - **Equipo:** A quién se le hará mantenimiento.
   - **Título:** Ej: "Limpieza interna y cambio de pasta térmica".
   - **Frecuencia:** Semanal, Mensual, Trimestral, Semestral o Anual.
   - **Última realización:** Fecha en que se hizo por última vez (si aplica).
   - **Técnico:** Responsable.
3. Guarda.

> 🔄 El sistema calcula automáticamente la **próxima fecha** de mantenimiento según la frecuencia.

### 5.3 Completar un mantenimiento preventivo
1. Ve al listado de mantenimientos preventivos.
2. Selecciona los que ya se realizaron.
3. En el menú desplegable superior elige **"Marcar mantenimientos seleccionados como completados"**.
4. El sistema actualizará la última fecha y calculará la siguiente automáticamente.

---

## 6. Licencias de Software

Controla las licencias de cada equipo (Windows, Office, antivirus, etc.).

### 6.1 Registrar una licencia
1. Ve a **Panel Admin → Inventario → Licencias de Software → Añadir**.
2. Completa:
   - **Equipo:** A qué computadora pertenece.
   - **Tipo:** Sistema Operativo, Office, Antivirus, CAD, Base de Datos, Otro.
   - **Nombre:** Ej: "Windows 11 Pro".
   - **Clave/Licencia:** El serial de activación.
   - **Fecha inicio:** Cuándo se activó.
   - **Fecha vencimiento:** Cuándo expira.
   - **Costo:** Precio de la licencia.
3. Guarda.

### 6.2 Ver licencias por vencer
- En el **Dashboard** aparecen las que vencen en 30 días.
- O visita **Menú → Licencias** para ver el listado completo: Activas, Por Vencer y Vencidas.

---

## 7. Alertas del Sistema

Las alertas se generan automáticamente. Para actualizarlas:

1. Ve al **Dashboard**.
2. Haz clic en el botón **"Verificar"** dentro del panel de Alertas Pendientes.
3. El sistema revisará:
   - Garantías por vencer (30 días).
   - Stock bajo.
   - Revisiones anuales pendientes.
   - Licencias por vencer.
   - Mantenimientos preventivos próximos.
4. Las nuevas alertas aparecerán en la lista.

### 7.1 Marcar alerta como leída
- En el Dashboard, haz clic en **"✓"** junto a cada alerta.
- O ve a **Panel Admin → Inventario → Alertas**, selecciona las que ya atendiste y usa **"Marcar alertas seleccionadas como leídas"**.

---

## 8. Reportes y Exportaciones

### 8.1 Reporte de equipos (PDF o Excel)
1. Ve al menú **"📊 Reportes"** o visita `/reportes/equipos/`.
2. Aplica filtros si necesitas:
   - Marca.
   - Estado (disponible, asignado, etc.).
   - Categoría.
   - Ubicación.
   - Rango de fechas.
3. Haz clic en:
   - **"Exportar PDF"** para descargar un documento formal.
   - **"Exportar Excel"** para descargar una hoja de cálculo editable.

### 8.2 Reporte de evidencias (PDF)
1. Ve a un equipo específico.
2. Si tiene evidencias fotográficas, busca la opción de generar reporte PDF.
3. Descarga el documento con todas las fotos y detalles.

---

## 9. Accesorios y Stock

### 9.1 Registrar un accesorio
1. Ve a **Panel Admin → Inventario → Accesorios → Añadir**.
2. Completa:
   - **Nombre:** Ej: "Mouse Logitech".
   - **Descripción:** Detalles.
   - **Cantidad:** Cuántas unidades hay en bodega.
   - **Stock mínimo:** Cantidad mínima antes de generar alerta.
3. Guarda.

### 9.2 Revisar stock crítico
- Aparece automáticamente en el Dashboard.
- O ve **Panel Admin → Inventario → Accesorios**. Los que están en rojo indican stock bajo.

### 9.3 Actualizar cantidad
1. Abre el accesorio.
2. Cambia el campo **"Cantidad"**.
3. Guarda.

---

## 10. Evidencias Fotográficas

Sube fotos de entregas, reparaciones o estado de equipos.

### 10.1 Subir evidencia
1. Ve al menú **"📸 Evidencia"** o visita `/evidencia/subir/`.
2. Selecciona:
   - **Equipo:** A qué equipo pertenece la foto.
   - **Tipo:** Entrega, Devolución, Reparación, Mantenimiento Preventivo o General.
   - **Descripción:** Breve texto.
   - **Imagen:** Archivo JPG o PNG.
3. Haz clic en **"Subir"**.

### 10.2 Ver evidencias de un equipo
1. Ve a la ficha pública del equipo (escaneando el QR o buscándolo).
2. En la sección "Evidencias" verás todas las fotos subidas.

---

## 11. Escaneo de Códigos QR

Cada equipo tiene un código QR único que lleva a su ficha pública.

### 11.1 Ver el QR de un equipo
1. Ve a **Panel Admin → Inventario → Equipos**.
2. Abre un equipo.
3. En la sección **"Código QR"** verás la imagen.
4. Haz clic para verla en tamaño completo.

### 11.2 Escanear con celular
1. Ve al menú **"📷 Escanear QR"** o visita `/escanear-qr/`.
2. Permite el acceso a la cámara.
3. Apunta al código QR del equipo.
4. Automáticamente se abrirá la ficha pública.

### 11.3 Ficha pública del equipo
Al escanear el QR o visitar la URL directa, cualquier persona puede ver:
- Nombre, marca, modelo, serial.
- Estado actual.
- Quién lo tiene asignado (si aplica).
- Historial de reparaciones.
- Licencias de software.
- Mantenimientos preventivos pendientes.
- Evidencias fotográficas.
- Historial de cambios (auditoría).

---

## 12. Métricas y Estadísticas

Visita **"📈 Métricas"** o `/metricas/` para ver estadísticas avanzadas:

### 12.1 KPIs superiores
- Total de reparaciones.
- Costo total gastado.
- Licencias por vencer.
- Licencias vencidas.

### 12.2 Gráficas
- **Costo por tipo de reparación:** ¿En qué se gasta más?
- **Equipos por categoría:** Distribución visual.
- **Equipos por ubicación:** Dónde está concentrado el inventario.
- **Equipos por estado:** Disponibles vs asignados vs reparación.

### 12.3 Tablas de ranking
- **Clientes con más equipos:** Quién tiene más asignado.
- **Equipos con más fallas:** Cuáles son los más problemáticos.

---

## 13. Roles de Usuario

El sistema tiene roles principales configurados:

| Rol | Permisos |
|-----|----------|
| **Administrador** | Acceso total: crear, editar, eliminar todo. Ver métricas. Administrar usuarios. |
| **Coordinador** | Crear y editar equipos, asignaciones, mantenimientos. Ver reportes. No eliminar. |
| **Técnico** | Registrar reparaciones, completar mantenimientos preventivos, subir evidencias. Ver equipos. |
| **Auditor** | Solo lectura. Puede ver todo pero no modificar. Ideal para revisiones de contabilidad. |

> 👤 Para asignar un rol, ve a **Panel Admin → Autenticación → Usuarios**, edita el usuario y agrégalo al grupo correspondiente.

---

## 14. Flujos de trabajo recomendados

### 14.1 Cuando compras un equipo nuevo
1. Admin → Equipos → Añadir.
2. Completa todos los campos (nombre, categoría, marca, modelo, serial, ubicación, garantía).
3. Sube foto si tienes.
4. Guarda. El sistema genera QR automáticamente.
5. Imprime el QR y pégalo en el equipo físico.

### 14.2 Cuando entregas un equipo a un empleado
1. Asegúrate de que el equipo esté **"Disponible"**.
2. Admin → Asignaciones → Añadir.
3. Selecciona equipo, cliente, ubicación física y accesorios entregados.
4. Guarda. El estado cambia a **"Asignado"** automáticamente.
5. Genera la Hoja de Responsabilidad.
6. Haz que el empleado firme digitalmente.
7. Entrega el equipo físico.

### 14.3 Cuando un equipo se daña
1. Admin → Cambios y Reparaciones → Añadir.
2. Registra el equipo, tipo de falla, descripción y técnico.
3. Si el equipo está asignado, reporta el fallo para cambiar su estado a **"En Reparación"**.
4. Cuando esté reparado, usa **"Reparar"** en el equipo para volverlo **"Disponible"**.

### 14.4 Cuando un equipo ya no sirve
1. Abre el equipo en el Admin.
2. Asegúrate de que esté **"Disponible"** o **"En Reparación"**.
3. Usa la acción **"Dar de Baja"**.
4. El equipo pasará a estado **"Dado de Baja"** y ya no aparecerá como disponible.

### 14.5 Revisión semanal recomendada (Lunes)
1. Abre el **Dashboard**.
2. Revisa **Alertas Pendientes**.
3. Revisa **Stock Crítico**.
4. Revisa **Mantenimientos Próximos**.
5. Haz clic en **"Verificar"** para actualizar alertas.
6. Atiende lo urgente.

---

## 15. Solución de problemas

### 15.1 "No puedo cambiar el estado de un equipo"
**Causa:** El sistema usa FSM (máquina de estados). No puedes escribir el estado directamente.  
**Solución:** Usa los botones de acción en la columna "Acciones" del listado de equipos.

### 15.2 "No aparece el QR de un equipo"
**Causa:** El QR se genera al guardar, pero a veces hay error de URL.  
**Solución:** Ve a `config/settings.py` y verifica que `SITE_URL` esté configurado correctamente.

### 15.3 "Las gráficas del Dashboard no cargan"
**Causa:** Problema de conexión a internet o bloqueo de scripts.  
**Solución:** Recarga la página (F5). Asegúrate de no tener bloqueadores de JavaScript.

### 15.4 "No puedo asignar un equipo"
**Causa:** El equipo no está en estado "Disponible".  
**Solución:** Verifica el estado. Si está "Asignado", "En Reparación" o "Dado de Baja", no se puede asignar hasta que vuelva a "Disponible".

### 15.5 "Las alertas no se actualizan"
**Causa:** Las alertas no se generan solas en tiempo real.  
**Solución:** Ve al Dashboard y haz clic en **"Verificar"** en el panel de Alertas Pendientes.

### 15.6 "Error al generar PDF"
**Causa:** Falta la librería `xhtml2pdf` o la plantilla HTML.  
**Solución:** Verifica que `xhtml2pdf` esté en `requirements.txt` y que exista la carpeta `templates/reportes/`.

### 15.7 "No puedo subir imágenes"
**Causa:** Configuración de `MEDIA_ROOT` o permisos de carpeta.  
**Solución:** Verifica que exista la carpeta `media/` y que el servidor tenga permisos de escritura.

---

## 📞 Soporte

Si encuentras un error que no está en esta lista:
1. Toma una captura de pantalla del error.
2. Anota los pasos que seguiste antes de que ocurriera.
3. Contacta al administrador del sistema con esa información.

---

**Fin del manual**
