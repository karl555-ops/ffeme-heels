from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="index"),
    path("productos/", views.productos, name="productos"),
    path("buscar/sugerencias/", views.buscar_sugerencias, name="buscar_sugerencias"),
    path("buscar/recientes/", views.busquedas_recientes, name="busquedas_recientes"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("logout/", views.logout_view, name="logout"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/agregar/<str:producto_id>/", views.agregar_wishlist, name="agregar_wishlist"),
    path("wishlist/eliminar/<str:producto_id>/", views.eliminar_wishlist, name="eliminar_wishlist"),
    path("sobre-nosotras/", views.sobre_nosotras, name="sobre_nosotras"),
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("carrito/", views.carrito, name="carrito"),
    path("carrito/agregar/<str:producto_id>/", views.agregar_carrito, name="agregar_carrito"),
    path("carrito/actualizar/<str:producto_id>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<str:producto_id>/", views.eliminar_carrito, name="eliminar_carrito"),
    path("perfil/", views.perfil, name="perfil"),
    path("checkout/", views.checkout_envio_pago, name="checkout_envio_pago"),
    path("factura/<int:orden_id>/", views.factura_detalle, name="factura_detalle"),
    path("producto/<str:producto_id>/", views.producto_detalle, name="producto_detalle"),
]
