from django.contrib import admin

from .models import DireccionEnvio, Factura, Orden, OrdenItem, PagoTarjeta, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color", "talla", "precio", "destacado", "creado_en")
    list_filter = ("color", "talla", "destacado")
    search_fields = ("nombre", "descripcion")


class OrdenItemInline(admin.TabularInline):
    model = OrdenItem
    extra = 0
    readonly_fields = ("producto_nombre", "producto_talla", "producto_precio", "cantidad", "subtotal")


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "subtotal", "envio", "total", "estado_envio", "creado_en")
    list_filter = ("estado_envio", "creado_en")
    search_fields = ("id", "usuario__username", "usuario__email")
    inlines = [OrdenItemInline]


@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre_completo", "telefono", "ciudad", "estado", "codigo_postal", "pais")
    search_fields = ("nombre_completo", "telefono", "ciudad", "estado", "codigo_postal")


@admin.register(PagoTarjeta)
class PagoTarjetaAdmin(admin.ModelAdmin):
    list_display = ("orden", "marca", "tipo", "titular", "ultimos_4", "referencia", "creado_en")
    list_filter = ("marca", "tipo", "creado_en")
    search_fields = ("titular", "ultimos_4", "referencia")


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("folio", "orden", "fecha", "razon_social", "rfc", "banco")
    search_fields = ("folio", "razon_social", "rfc", "orden__id")
