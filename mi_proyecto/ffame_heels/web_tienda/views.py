from decimal import Decimal
import random

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegistroForm
from .models import DireccionEnvio, Factura, Orden, OrdenItem, PagoTarjeta, Producto


User = get_user_model()
ENVIO_GRATIS_UMBRAL = Decimal("6000.00")
COSTO_ENVIO = Decimal("200.00")

PRODUCTOS_MOCK = [
    {
        "id": "mock-tacon-siletto-grande",
        "nombre": "Tacón Siletto Grande",
        "precio": Decimal("2400.00"),
        "imagen": "imagenes/tacon sileto grande.jpg",
        "categoria": "siletto",
        "descripcion": "Tacón estilizado para ocasiones especiales.",
        "talla": "4",
        "destacado": True,
        "es_nuevo": True,
    },
    {
        "id": "mock-tacon-kitten-piedreria",
        "nombre": "Tacón Kitten con Piedrería",
        "precio": Decimal("2775.00"),
        "imagen": "imagenes/Tacon kitten con correa de piedreria.jpg",
        "categoria": "kitten",
        "descripcion": "Diseño cómodo y elegante con acabado brillante.",
        "talla": "5",
        "destacado": True,
        "es_nuevo": True,
    },
    {
        "id": "mock-botin-tacon-redondo",
        "nombre": "Botín de Tacón Redondo",
        "precio": Decimal("2300.00"),
        "imagen": "imagenes/botin de tacon redondo.jpg",
        "categoria": "botin",
        "descripcion": "Botín versátil para looks urbanos y sofisticados.",
        "talla": "5",
        "destacado": False,
        "es_nuevo": True,
    },
    {
        "id": "mock-bota-alta",
        "nombre": "Bota Alta",
        "precio": Decimal("1940.00"),
        "imagen": "imagenes/bota alta.jpg",
        "categoria": "bota",
        "descripcion": "Bota alta clásica para temporada de frío.",
        "talla": "6",
        "destacado": False,
        "es_nuevo": False,
    },
]

CATEGORIAS_MOCK = [
    {"slug": "siletto", "nombre": "Siletto"},
    {"slug": "kitten", "nombre": "Kitten"},
    {"slug": "botin", "nombre": "Botines"},
    {"slug": "bota", "nombre": "Botas"},
]


def _obtener_carrito_sesion(request):
    return request.session.get("carrito", {})


def _guardar_carrito_sesion(request, carrito):
    request.session["carrito"] = carrito
    request.session.modified = True


def _obtener_wishlist_sesion(request):
    return request.session.get("wishlist", [])


def _guardar_wishlist_sesion(request, wishlist):
    request.session["wishlist"] = wishlist
    request.session.modified = True


def _producto_mock_por_id(producto_id):
    producto_id = str(producto_id)
    for producto in PRODUCTOS_MOCK:
        if producto["id"] == producto_id:
            return producto
    return None


def _es_id_mock(producto_id):
    return str(producto_id).startswith("mock-")


def _serialize_producto_mock(producto):
    return {
        "id": producto["id"],
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "descripcion": producto.get("descripcion", ""),
        "talla": producto.get("talla", ""),
        "es_nuevo": producto.get("es_nuevo", False),
        "is_mock": True,
        "imagen_url": f"/static/{producto['imagen']}",
        "categoria": producto.get("categoria", ""),
        "destacado": producto.get("destacado", False),
    }


def _serialize_producto_real(producto):
    return {
        "id": str(producto.id),
        "nombre": producto.nombre,
        "precio": producto.precio,
        "descripcion": producto.descripcion,
        "talla": getattr(producto, "talla", ""),
        "es_nuevo": getattr(producto, "es_nuevo", False),
        "is_mock": False,
        "imagen_url": producto.imagen.url if getattr(producto, "imagen", None) else "",
        "categoria": "",
        "destacado": getattr(producto, "destacado", False),
    }


def _producto_unificado_por_id(producto_id):
    producto_id = str(producto_id)
    if _es_id_mock(producto_id):
        producto = _producto_mock_por_id(producto_id)
        if not producto:
            raise Http404("Producto mock no encontrado")
        return _serialize_producto_mock(producto)

    producto_real = get_object_or_404(Producto, id=int(producto_id))
    return _serialize_producto_real(producto_real)


def _catalogo_unificado():
    productos_db = list(Producto.objects.all())
    if productos_db:
        return [_serialize_producto_real(p) for p in productos_db], False
    return [_serialize_producto_mock(p) for p in PRODUCTOS_MOCK], True


def _carrito_items_y_totales(request):
    carrito = _obtener_carrito_sesion(request)
    items = []
    subtotal = Decimal("0.00")

    for producto_id, cantidad in carrito.items():
        try:
            producto = _producto_unificado_por_id(producto_id)
        except Exception:
            continue

        cantidad_int = int(cantidad)
        item_subtotal = Decimal(producto["precio"]) * cantidad_int
        subtotal += item_subtotal

        items.append(
            {
                "producto": producto,
                "cantidad": cantidad_int,
                "subtotal": item_subtotal,
            }
        )

    envio = Decimal("0.00") if subtotal >= ENVIO_GRATIS_UMBRAL else COSTO_ENVIO
    total = subtotal + envio
    carrito_count = sum(int(c) for c in carrito.values())

    return {
        "items": items,
        "subtotal": subtotal,
        "envio": envio,
        "total": total,
        "carrito_count": carrito_count,
        "umbral_envio_gratis": ENVIO_GRATIS_UMBRAL,
    }


def inicio(request):
    catalogo, es_mock = _catalogo_unificado()
    novedades = [p for p in catalogo if p.get("destacado")] or catalogo[:6]
    colecciones = catalogo[:8]

    context = {
        "novedades": novedades,
        "colecciones": colecciones,
        "catalogo_es_mock": es_mock,
        "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
    }
    return render(request, "index.html", context)


def _normalizar_query(texto):
    return " ".join((texto or "").strip().split())


def _obtener_busquedas_recientes(request):
    recientes = request.session.get("busquedas_recientes", [])
    if not isinstance(recientes, list):
        return []
    limpias = []
    for item in recientes:
        q = _normalizar_query(item)
        if q:
            limpias.append(q)
    return limpias[:8]


def _guardar_busqueda_reciente(request, query):
    q = _normalizar_query(query)
    if not q:
        return

    recientes = _obtener_busquedas_recientes(request)
    recientes = [x for x in recientes if x.lower() != q.lower()]
    recientes.insert(0, q)
    request.session["busquedas_recientes"] = recientes[:8]
    request.session.modified = True


def _sugerencias_busqueda(request, q, limit=8):
    qn = _normalizar_query(q).lower()
    catalogo, _ = _catalogo_unificado()

    nombres = []
    categorias = set()
    for p in catalogo:
        nombre = str(p.get("nombre", "")).strip()
        categoria = str(p.get("categoria", "")).strip()
        if categoria:
            categorias.add(categoria)

        if not nombre:
            continue

        if not qn or qn in nombre.lower() or qn in str(p.get("descripcion", "")).lower():
            nombres.append(nombre)

    if qn:
        cat_matches = [c.title() for c in sorted(categorias) if qn in c.lower()]
    else:
        cat_matches = [c.title() for c in sorted(categorias)]

    sugerencias = []
    for nombre in nombres:
        if nombre not in sugerencias:
            sugerencias.append(nombre)
        if len(sugerencias) >= limit:
            break

    for cat in cat_matches:
        if cat not in sugerencias:
            sugerencias.append(cat)
        if len(sugerencias) >= limit:
            break

    return sugerencias[:limit]


def buscar_sugerencias(request):
    q = request.GET.get("q", "")
    sugerencias = _sugerencias_busqueda(request, q, limit=8)
    recientes = _obtener_busquedas_recientes(request)
    return JsonResponse(
        {
            "query": _normalizar_query(q),
            "sugerencias": sugerencias,
            "recientes": recientes,
        }
    )


def busquedas_recientes(request):
    if request.method == "POST":
        q = request.POST.get("q", "")
        _guardar_busqueda_reciente(request, q)
        return JsonResponse({"ok": True, "recientes": _obtener_busquedas_recientes(request)})

    return JsonResponse({"recientes": _obtener_busquedas_recientes(request)})


def productos(request):
    categoria = request.GET.get("categoria", "").strip()
    precio = request.GET.get("precio", "").strip()
    orden = request.GET.get("orden", "nuevo").strip()
    q = request.GET.get("q", "").strip()
    if q:
        _guardar_busqueda_reciente(request, q)

    lista_productos, es_mock = _catalogo_unificado()

    if q:
        q_lower = q.lower()
        lista_productos = [
            p for p in lista_productos
            if q_lower in str(p.get("nombre", "")).lower()
            or q_lower in str(p.get("descripcion", "")).lower()
        ]

    if categoria:
        lista_productos = [p for p in lista_productos if p.get("categoria") == categoria]

    if precio == "1900-2500":
        lista_productos = [p for p in lista_productos if Decimal("1900.00") <= Decimal(p["precio"]) <= Decimal("2500.00")]
    elif precio == "2500-3500":
        lista_productos = [p for p in lista_productos if Decimal("2500.00") <= Decimal(p["precio"]) <= Decimal("3500.00")]
    elif precio == "3500-99999":
        lista_productos = [p for p in lista_productos if Decimal(p["precio"]) >= Decimal("3500.00")]

    if orden == "precio_asc":
        lista_productos = sorted(lista_productos, key=lambda p: Decimal(p["precio"]))
    elif orden == "precio_desc":
        lista_productos = sorted(lista_productos, key=lambda p: Decimal(p["precio"]), reverse=True)
    elif orden == "nombre":
        lista_productos = sorted(lista_productos, key=lambda p: p["nombre"].lower())

    paginator = Paginator(lista_productos, 8)
    page_number = request.GET.get("page")
    productos_page = paginator.get_page(page_number)

    return render(
        request,
        "productos.html",
        {
            "productos": productos_page,
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
            "categorias": CATEGORIAS_MOCK if es_mock else [],
            "categoria_actual": categoria,
            "precio_actual": precio,
            "orden": orden if orden else "nuevo",
            "q": q,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    login_form = LoginForm()
    registro_form = RegistroForm()

    if request.method == "POST" and request.POST.get("form_type") == "login":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            identificador = login_form.cleaned_data["identificador"].strip()
            password = login_form.cleaned_data["password"]

            username = identificador
            if "@" in identificador:
                user_by_email = User.objects.filter(email__iexact=identificador).first()
                if user_by_email:
                    username = user_by_email.username

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Inicio de sesión exitoso.")
                return redirect("index")

            login_form.add_error(None, "Credenciales inválidas. Verifica tus datos.")

    return render(
        request,
        "login.html",
        {
            "login_form": login_form,
            "registro_form": registro_form,
            "active_tab": "login",
        },
    )


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    login_form = LoginForm()
    registro_form = RegistroForm()

    if request.method == "POST" and request.POST.get("form_type") == "registro":
        registro_form = RegistroForm(request.POST)
        if registro_form.is_valid():
            user = User.objects.create_user(
                username=registro_form.cleaned_data["username"],
                email=registro_form.cleaned_data["email"],
                password=registro_form.cleaned_data["password1"],
            )
            login(request, user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("index")

    return render(
        request,
        "login.html",
        {
            "login_form": login_form,
            "registro_form": registro_form,
            "active_tab": "registro",
        },
    )


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("index")


def wishlist(request):
    wishlist_ids = _obtener_wishlist_sesion(request)
    productos_wishlist = []

    for pid in wishlist_ids:
        try:
            productos_wishlist.append(_producto_unificado_por_id(pid))
        except Exception:
            continue

    return render(
        request,
        "wishlist.html",
        {
            "productos": productos_wishlist,
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )


def agregar_wishlist(request, producto_id):
    if request.method != "POST":
        return redirect("producto_detalle", producto_id=producto_id)

    _producto_unificado_por_id(producto_id)
    producto_id = str(producto_id)

    wishlist = _obtener_wishlist_sesion(request)
    if producto_id not in [str(x) for x in wishlist]:
        wishlist.append(producto_id)
        _guardar_wishlist_sesion(request, wishlist)

    return redirect(request.META.get("HTTP_REFERER", "wishlist"))


def eliminar_wishlist(request, producto_id):
    if request.method != "POST":
        return redirect("wishlist")

    producto_id = str(producto_id)
    wishlist = [str(x) for x in _obtener_wishlist_sesion(request)]
    if producto_id in wishlist:
        wishlist.remove(producto_id)
        _guardar_wishlist_sesion(request, wishlist)

    return redirect("wishlist")


def sobre_nosotras(request):
    return render(
        request,
        "sobre_nosotras.html",
        {
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )


def devoluciones(request):
    return render(request, "devoluciones.html", {
        "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
    })


def envios(request):
    return render(request, "envios.html", {
        "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
    })


def soporte(request):
    return render(request, "soporte.html", {
        "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
    })


@login_required(login_url="login")
def notificaciones(request):
    notificaciones_data = [
        {
            "titulo": "Bienvenida a FFeme Heels",
            "mensaje": "Tu cuenta está activa. Explora nuestras novedades y colecciones.",
            "tipo": "info",
        },
        {
            "titulo": "Wishlist disponible",
            "mensaje": "Ahora puedes guardar tus productos favoritos en tu wishlist.",
            "tipo": "wishlist",
        },
        {
            "titulo": "Envío gratis",
            "mensaje": "Obtén envío gratis en compras mayores a $6,000 MXN.",
            "tipo": "promo",
        },
    ]
    return render(
        request,
        "notificaciones.html",
        {
            "notificaciones": notificaciones_data,
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )


def carrito(request):
    contexto = _carrito_items_y_totales(request)
    return render(request, "carrito.html", contexto)


def agregar_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("producto_detalle", producto_id=producto_id)

    _producto_unificado_por_id(producto_id)

    carrito = _obtener_carrito_sesion(request)
    key = str(producto_id)
    carrito[key] = int(carrito.get(key, 0)) + 1
    _guardar_carrito_sesion(request, carrito)

    return redirect("carrito")


def actualizar_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("carrito")

    carrito = _obtener_carrito_sesion(request)
    key = str(producto_id)
    accion = request.POST.get("accion")

    if key in carrito:
        if accion == "sumar":
            carrito[key] = int(carrito[key]) + 1
        elif accion == "restar":
            carrito[key] = int(carrito[key]) - 1
            if carrito[key] <= 0:
                del carrito[key]

    _guardar_carrito_sesion(request, carrito)
    return redirect("carrito")


def eliminar_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("carrito")

    carrito = _obtener_carrito_sesion(request)
    key = str(producto_id)
    if key in carrito:
        del carrito[key]
        _guardar_carrito_sesion(request, carrito)

    return redirect("carrito")


@login_required(login_url="login")
def perfil(request):
    user = request.user
    return render(
        request,
        "perfil.html",
        {
            "perfil_usuario": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_joined": user.date_joined,
            },
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )


def checkout_envio_pago(request):
    contexto_carrito = _carrito_items_y_totales(request)
    if not contexto_carrito["items"]:
        messages.info(request, "Tu carrito está vacío. Agrega productos para continuar.")
        return redirect("carrito")

    estados_mexico = [
        "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
        "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila", "Colima", "Durango",
        "Estado de México", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco",
        "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla",
        "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora",
        "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas",
    ]

    if request.method == "POST":
        nombre_completo = request.POST.get("nombre_completo", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        calle = request.POST.get("calle", "").strip()
        colonia = request.POST.get("colonia", "").strip()
        ciudad = request.POST.get("ciudad", "").strip()
        estado = request.POST.get("estado", "").strip()
        codigo_postal = request.POST.get("codigo_postal", "").strip()

        tarjeta_titular = request.POST.get("tarjeta_titular", "").strip()
        tarjeta_numero = request.POST.get("tarjeta_numero", "").replace(" ", "").strip()
        tarjeta_marca = request.POST.get("tarjeta_marca", "").strip().lower()
        tarjeta_tipo = request.POST.get("tarjeta_tipo", "").strip().lower()

        razon_social = request.POST.get("razon_social", "").strip() or "Cliente FFAME HEELS"
        rfc = request.POST.get("rfc", "").strip()

        errores = []
        if not all([nombre_completo, telefono, calle, colonia, ciudad, estado, codigo_postal]):
            errores.append("Completa todos los campos de envío.")
        if estado not in estados_mexico:
            errores.append("Selecciona un estado válido de México.")
        if tarjeta_marca not in [PagoTarjeta.MARCA_VISA, PagoTarjeta.MARCA_MASTERCARD]:
            errores.append("Solo se aceptan tarjetas Visa o Mastercard.")
        if tarjeta_tipo not in [PagoTarjeta.TIPO_CREDITO, PagoTarjeta.TIPO_DEBITO]:
            errores.append("Selecciona tipo de tarjeta: crédito o débito.")
        if len(tarjeta_numero) < 13 or not tarjeta_numero.isdigit():
            errores.append("Ingresa un número de tarjeta válido.")
        if len(codigo_postal) < 5:
            errores.append("Ingresa un código postal válido.")

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            orden = Orden.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                subtotal=contexto_carrito["subtotal"],
                envio=contexto_carrito["envio"],
                total=contexto_carrito["total"],
                estado_envio=Orden.ESTADO_PENDIENTE,
            )

            for item in contexto_carrito["items"]:
                OrdenItem.objects.create(
                    orden=orden,
                    producto_nombre=item["producto"]["nombre"],
                    producto_talla=item["producto"].get("talla", ""),
                    producto_precio=item["producto"]["precio"],
                    cantidad=item["cantidad"],
                    subtotal=item["subtotal"],
                )

            DireccionEnvio.objects.create(
                orden=orden,
                nombre_completo=nombre_completo,
                telefono=telefono,
                calle=calle,
                colonia=colonia,
                ciudad=ciudad,
                estado=estado,
                codigo_postal=codigo_postal,
                pais="México",
            )

            referencia = f"PAY-{orden.id}-{random.randint(1000, 9999)}"
            PagoTarjeta.objects.create(
                orden=orden,
                marca=tarjeta_marca,
                tipo=tarjeta_tipo,
                titular=tarjeta_titular or nombre_completo,
                ultimos_4=tarjeta_numero[-4:],
                referencia=referencia,
            )

            folio = f"FAC-{orden.id:06d}"
            Factura.objects.create(
                orden=orden,
                folio=folio,
                razon_social=razon_social,
                rfc=rfc,
            )

            _guardar_carrito_sesion(request, {})
            messages.success(request, "Pedido confirmado. Tu factura se generó correctamente.")
            return redirect("factura_detalle", orden_id=orden.id)

    return render(
        request,
        "checkout.html",
        {
            "items": contexto_carrito["items"],
            "subtotal": contexto_carrito["subtotal"],
            "envio": contexto_carrito["envio"],
            "total": contexto_carrito["total"],
            "carrito_count": contexto_carrito["carrito_count"],
            "estados_mexico": estados_mexico,
        },
    )


def factura_detalle(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    direccion = getattr(orden, "direccion_envio", None)
    pago = getattr(orden, "pago", None)
    factura = getattr(orden, "factura", None)
    items = orden.items.all()

    iva_monto = Decimal(orden.total) * Decimal("0.16")
    total_con_iva = Decimal(orden.total) + iva_monto

    return render(
        request,
        "factura.html",
        {
            "orden": orden,
            "direccion": direccion,
            "pago": pago,
            "factura": factura,
            "items": items,
            "subtotal": orden.subtotal,
            "iva_monto": iva_monto,
            "total_con_iva": total_con_iva,
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )


def producto_detalle(request, producto_id):
    producto = _producto_unificado_por_id(producto_id)
    return render(
        request,
        "producto_detalle.html",
        {
            "producto": producto,
            "carrito_count": _carrito_items_y_totales(request)["carrito_count"],
        },
    )
