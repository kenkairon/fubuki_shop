from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Cliente, Pedido, LineaPedido, Producto


class ErrorPedido(Exception):
    pass


@transaction.atomic
def crear_pedido(datos, items, fecha=None):
    unidades = sum(items.values())
    if unidades == 0:
        raise ErrorPedido("Tu carrito está vacío.")
    especial = unidades > settings.LIMITE_UNIDADES
    if (especial or fecha) and not fecha:
        raise ErrorPedido("Indica la fecha de entrega.")
    if fecha and fecha < timezone.now() + timedelta(hours=settings.HORAS_ANTICIPACION):
        raise ErrorPedido("Los pedidos agendados necesitan al menos 48 horas de anticipación.")

    cumple = datos.get("cumpleanos")
    if isinstance(cumple, str):
        cumple = parse_date(cumple) if cumple else None
    cliente, creado = Cliente.objects.get_or_create(
        email=datos["email"],
        defaults={"nombre": datos["nombre"], "telefono": datos["telefono"],
                  "cumpleanos": cumple})
    if not creado and cumple and not cliente.cumpleanos:
        cliente.cumpleanos = cumple
        cliente.save(update_fields=["cumpleanos"])
    prods = {p.id: p for p in Producto.objects.select_for_update()
             .filter(id__in=[int(i) for i in items], activo=True)}
    tipo = "ESP" if especial else "AGE" if fecha else "INM"
    pedido = Pedido.objects.create(cliente=cliente, tipo=tipo, fecha_entrega=fecha,
                                   notas=datos.get("notas", ""))
    subtotal = Decimal(0)
    for pid, cant in items.items():
        p = prods.get(int(pid))
        if not p:
            raise ErrorPedido("Un producto ya no está disponible.")
        if not especial:  # los especiales se coordinan contigo
            if p.stock < cant:
                raise ErrorPedido(f"'{p.nombre}' no tiene stock suficiente ({p.stock} disp.).")
            p.stock -= cant
            p.save(update_fields=["stock"])
        LineaPedido.objects.create(pedido=pedido, producto=p, cantidad=cant, precio_unitario=p.precio)
        subtotal += p.precio * cant

    descuento = Decimal(0)
    if (cliente.compras_completadas + 1) % settings.COMPRAS_PARA_DESCUENTO == 0:
        descuento = subtotal * settings.PORCENTAJE_DESCUENTO / 100
    hoy = timezone.localdate()
    pedido.regalo_cumple = bool(cliente.cumpleanos and cliente.cumpleanos.month == hoy.month)
    pedido.subtotal, pedido.descuento, pedido.total = subtotal, descuento, subtotal - descuento
    pedido.save()
    cliente.compras_completadas += 1
    cliente.save(update_fields=["compras_completadas"])
    return pedido