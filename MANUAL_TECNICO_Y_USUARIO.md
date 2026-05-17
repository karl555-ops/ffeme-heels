# Manual Técnico y de Usuario  
## Proyecto: FFAME Heels (Tienda Web de Calzado)

---

## 1. Introducción

Este documento reúne la información esencial para:
- **Manual técnico**: instalación, estructura, arquitectura, componentes y mantenimiento del sistema.
- **Manual de usuario**: uso funcional de la tienda web por parte del cliente final y del administrador básico.

El proyecto está basado en **Django** y organiza su lógica principal en la app **web_tienda**, con plantillas HTML y recursos estáticos (CSS e imágenes).

---

## 2. Objetivo del sistema

Implementar una tienda web enfocada en la visualización y gestión básica de productos de calzado (tacones, botines, botas, etc.), permitiendo interacción del usuario mediante páginas de:
- inicio
- listado de productos
- detalle de producto
- carrito
- wishlist
- perfil
- notificaciones
- autenticación (login)
- página informativa “sobre nosotras”

---

## 3. Alcance funcional

### Funcionalidades principales identificadas
- Navegación entre páginas de catálogo y contenido informativo.
- Visualización de productos y detalle individual.
- Interfaces para carrito y lista de deseos (wishlist).
- Secciones de perfil y notificaciones.
- Administración de datos desde Django Admin (modelos de `web_tienda`).
- Uso de formularios definidos en `forms.py`.

### Módulos clave
- **Proyecto Django**: `mi_proyecto/ffame_heels/ffame_heels`
- **Aplicación principal**: `mi_proyecto/ffame_heels/web_tienda`
- **Frontend estático**: `ffemeh/templates` y `ffemeh/static`

---

## 4. Arquitectura técnica

### 4.1 Patrón aplicado
Se sigue el patrón **MVT (Model - View - Template)** de Django:
- **Model**: estructura de datos en `models.py`.
- **View**: lógica de negocio y flujo HTTP en `views.py`.
- **Template**: renderizado de interfaz en archivos `.html`.

### 4.2 Flujo general de una petición
1. El usuario solicita una URL.
2. Django enruta la petición por `urls.py`.
3. Se ejecuta la vista correspondiente (`views.py`).
4. La vista consulta/transforma datos (si aplica) con modelos/formularios.
5. Se renderiza una plantilla HTML con contexto.
6. Se envía la respuesta al navegador.

---

## 5. Estructura de carpetas (resumen)

```text
mi_proyecto/
└── ffame_heels/
    ├── manage.py
    ├── db.sqlite3
    ├── ffame_heels/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    └── web_tienda/
        ├── admin.py
        ├── apps.py
        ├── forms.py
        ├── models.py
        ├── urls.py
        ├── views.py
        └── migrations/

ffemeh/
├── templates/
│   ├── index.html
│   ├── productos.html
│   ├── producto_detalle.html
│   ├── carrito.html
│   ├── wishlist.html
│   ├── login.html
│   ├── perfil.html
│   ├── notificaciones.html
│   └── sobre_nosotras.html
└── static/
    ├── css/estilos.css
    ├── css/css/estilos.css
    ├── iconos/
    └── imagenes/
```

---

## 6. Requisitos técnicos

### 6.1 Software requerido
- Python 3.10+ (recomendado)
- pip
- Django (versión compatible con el proyecto)
- SQLite (incluido por defecto al usar `db.sqlite3`)

### 6.2 Entorno recomendado
- Sistema operativo: Windows/Linux/macOS
- Editor: VS Code (opcional)
- Navegador actualizado (Chrome/Edge/Firefox)

---

## 7. Instalación y despliegue local (manual técnico)

1. Abrir terminal en:
   ```bash
   mi_proyecto/ffame_heels
   ```

2. Crear y activar entorno virtual:
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Instalar dependencias:
   ```bash
   pip install django
   ```

4. Aplicar migraciones:
   ```bash
   python manage.py migrate
   ```

5. Crear superusuario (opcional para admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Ejecutar servidor:
   ```bash
   python manage.py runserver
   ```

7. Abrir en navegador:
   - Sitio: `http://127.0.0.1:8000/`
   - Admin: `http://127.0.0.1:8000/admin/`

---

## 8. Configuración principal

### 8.1 `settings.py`
Debe contener configuración de:
- `INSTALLED_APPS` con `web_tienda`
- plantillas (TEMPLATES)
- archivos estáticos (`STATIC_URL`, rutas de static)
- base de datos (SQLite)

### 8.2 `urls.py` del proyecto
Debe incluir rutas de la app:
- inclusión de `web_tienda.urls`
- ruta de administración `admin/`

### 8.3 `urls.py` de la app
Define las rutas funcionales hacia vistas de:
- inicio
- productos
- detalle
- carrito
- wishlist
- login
- perfil
- notificaciones
- sobre nosotras

---

## 9. Modelos, vistas y formularios (manual técnico)

### 9.1 `models.py`
Contiene las entidades de negocio del ecommerce (por ejemplo: productos, categorías, etc., según implementación actual).

### 9.2 `views.py`
Contiene las funciones/clases que:
- reciben request
- procesan datos
- renderizan plantillas o redirigen

### 9.3 `forms.py`
Define formularios de captura/validación para operaciones del sistema (autenticación, filtros, contacto u otros que estén implementados).

### 9.4 `admin.py`
Registra modelos para administración en panel Django Admin.

---

## 10. Frontend y recursos estáticos

### Plantillas HTML
Ubicación: `ffemeh/templates/`

Principales páginas:
- `index.html` → portada
- `productos.html` → catálogo
- `producto_detalle.html` → vista de detalle
- `carrito.html` → carrito
- `wishlist.html` → favoritos
- `login.html` → autenticación
- `perfil.html` → perfil
- `notificaciones.html` → mensajes/notificaciones
- `sobre_nosotras.html` → información institucional

### Estilos e imágenes
- CSS: `ffemeh/static/css/estilos.css` (y variante en `css/css/estilos.css`)
- Imágenes: `ffemeh/static/imagenes/`
- Iconos: `ffemeh/static/iconos/`

---

## 11. Seguridad y buenas prácticas (técnico)

- No exponer `SECRET_KEY` en repositorios públicos.
- Mantener `DEBUG = False` en producción.
- Restringir `ALLOWED_HOSTS` en producción.
- Validar formularios con métodos seguros de Django.
- Usar HTTPS en despliegue real.
- Respaldar base de datos periódicamente.
- Aplicar migraciones controladas por entorno.

---

## 12. Mantenimiento y soporte (técnico)

### Tareas recurrentes
- Revisar logs de errores.
- Actualizar dependencias y parches de seguridad.
- Ejecutar pruebas funcionales tras cambios.
- Verificar integridad de migraciones.
- Optimizar carga de imágenes estáticas.

### Respaldo básico
- Copia de `db.sqlite3`
- Copia de código fuente completo
- Versionado con Git recomendado

---

## 13. Manual de usuario

## 13.1 Perfil del usuario final
Cliente que navega la tienda para conocer productos y gestionar intereses de compra.

## 13.2 Ingreso al sistema
1. Abrir navegador.
2. Acceder a la URL del sitio.
3. Desde la navegación principal puede entrar a:
   - Inicio
   - Productos
   - Carrito
   - Wishlist
   - Login/Perfil

## 13.3 Uso de las pantallas

### Inicio (`index.html`)
- Muestra portada, banners y accesos principales al catálogo.

### Productos (`productos.html`)
- Permite visualizar el listado de artículos disponibles.

### Detalle de producto (`producto_detalle.html`)
- Muestra información ampliada de un producto concreto (imagen, nombre, etc. según diseño).

### Carrito (`carrito.html`)
- Vista de los productos seleccionados para posible compra.

### Wishlist (`wishlist.html`)
- Lista de productos guardados como favoritos/interés.

### Login (`login.html`)
- Pantalla de acceso/autenticación del usuario.

### Perfil (`perfil.html`)
- Consulta de información personal del usuario (según funcionalidades activas).

### Notificaciones (`notificaciones.html`)
- Muestra avisos o mensajes relevantes del sistema.

### Sobre nosotras (`sobre_nosotras.html`)
- Información de marca/equipo y propósito de la tienda.

---

## 13.4 Flujo de uso recomendado
1. Entrar al inicio.
2. Ir a productos.
3. Abrir detalle del producto de interés.
4. Agregar a carrito o wishlist (si está implementado en la lógica activa).
5. Iniciar sesión para acciones de cuenta (si aplica).

---

## 14. Solución de problemas comunes

### 1) El servidor no inicia
- Verificar entorno virtual activo.
- Confirmar instalación de Django.
- Revisar puerto ocupado (`runserver 8001` como alternativa).

### 2) No cargan estilos/imágenes
- Verificar configuración de `STATIC_URL` y rutas de static.
- Confirmar ubicación real de archivos en `ffemeh/static`.

### 3) Error de base de datos
- Ejecutar:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### 4) Error 404 en páginas
- Revisar rutas en `urls.py` (proyecto y app).
- Verificar nombre correcto de vistas y templates.

---

## 15. Glosario breve

- **Django**: framework web en Python.
- **MVT**: arquitectura Model-View-Template.
- **Migración**: cambios versionados de esquema de BD.
- **Admin**: panel administrativo nativo de Django.
- **Static**: archivos estáticos (CSS, imágenes, JS).
- **Template**: archivo HTML renderizado por Django.

---

## 16. Conclusión

El sistema FFAME Heels cuenta con una base sólida para ecommerce, organizada con Django y separada en componentes técnicos y de interfaz.  
Este manual concentra los lineamientos mínimos y suficientes para operar, mantener y usar la plataforma tanto desde el punto de vista técnico como de usuario final.
