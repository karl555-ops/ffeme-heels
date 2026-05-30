from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class SubCategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="subcategorias")
    nombre = models.CharField(max_length=80)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"

    def __str__(self):
        return f"{self.categoria.nombre} › {self.nombre}"


class Producto(models.Model):
    COLOR_BLANCO = "blanco"
    COLOR_NEGRO = "negro"
    COLOR_AZUL = "azul"
    COLOR_BORGONA = "borgona"
    COLOR_MARRON = "marron"

    COLOR_CHOICES = [
        (COLOR_BLANCO, "Blanco"),
        (COLOR_NEGRO, "Negro"),
        (COLOR_AZUL, "Azul"),
        (COLOR_BORGONA, "Borgoña"),
        (COLOR_MARRON, "Marrón"),
    ]

    TALLA_3 = "3"
    TALLA_4 = "4"
    TALLA_5 = "5"
    TALLA_6 = "6"

    TALLA_CHOICES = [
        (TALLA_3, "3"),
        (TALLA_4, "4"),
        (TALLA_5, "5"),
        (TALLA_6, "6"),
    ]

    subcategoria = models.ForeignKey(
        SubCategoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
        verbose_name="Subcategoría",
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="productos/")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default=COLOR_NEGRO)
    talla = models.CharField(max_length=2, choices=TALLA_CHOICES, default=TALLA_3)
    destacado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.nombre} - {self.get_color_display()} - Talla {self.talla}"


class Orden(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PREPARANDO = "preparando"
    ESTADO_ENVIADO = "enviado"
    ESTADO_ENTREGADO = "entregado"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PREPARANDO, "Preparando"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ENTREGADO, "Entregado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes",
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_envio = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Orden #{self.id} - {self.get_estado_envio_display()}"


class DireccionEnvio(models.Model):
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="direccion_envio")
    nombre_completo = models.CharField(max_length=140)
    telefono = models.CharField(max_length=20)
    calle = models.CharField(max_length=160)
    colonia = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=120)
    estado = models.CharField(max_length=120)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=60, default="México")

    def __str__(self):
        return f"{self.nombre_completo} - {self.ciudad}, {self.estado}"


class PagoTarjeta(models.Model):
    MARCA_VISA = "visa"
    MARCA_MASTERCARD = "mastercard"
    MARCA_CHOICES = [
        (MARCA_VISA, "Visa"),
        (MARCA_MASTERCARD, "Mastercard"),
    ]

    TIPO_CREDITO = "credito"
    TIPO_DEBITO = "debito"
    TIPO_CHOICES = [
        (TIPO_CREDITO, "Crédito"),
        (TIPO_DEBITO, "Débito"),
    ]

    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="pago")
    marca = models.CharField(max_length=20, choices=MARCA_CHOICES)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titular = models.CharField(max_length=140)
    ultimos_4 = models.CharField(max_length=4)
    referencia = models.CharField(max_length=40, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_marca_display()} {self.get_tipo_display()} ****{self.ultimos_4}"


class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="items")
    producto_nombre = models.CharField(max_length=160)
    producto_talla = models.CharField(max_length=20, blank=True)
    producto_precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto_nombre} x{self.cantidad}"


class Factura(models.Model):
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="factura")
    folio = models.CharField(max_length=30, unique=True)
    fecha = models.DateField(auto_now_add=True)
    razon_social = models.CharField(max_length=150, default="Cliente FFAME HEELS")
    rfc = models.CharField(max_length=13, blank=True)
    banco = models.CharField(max_length=80, default="BBVA México")
    numero_cuenta = models.CharField(max_length=30, default="**** **** **** 1234")
    titular_cuenta = models.CharField(max_length=150, default="FFAME HEELS SA DE CV")
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)

    def __str__(self):
        return f"Factura {self.folio}"
