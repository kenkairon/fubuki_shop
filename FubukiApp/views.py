from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .carrito import Carrito
from .models import Producto, Resena, Sugerencia
from .servicios import crear_pedido, ErrorPedido


def inicio(request):
    return render(request, "FubukiApp/inicio.html", {
        "destacados": Producto.objects.filter(activo=True, es_combo=False)[:3],
        "combos": Producto.objects.filter(activo=True, es_combo=True)[:3],
        "resenas": Resena.objects.filter(aprobada=True).order_by("-creado")[:4]})


def productos(request):
    return render(request, "FubukiApp/productos.html", {
        "titulo": "Productos", "lista": Producto.objects.filter(activo=True, es_combo=False)})


def promociones(request):
    return render(request, "FubukiApp/productos.html", {
        "titulo": "Promociones", "lista": Producto.objects.filter(activo=True, es_combo=True)})


def agregar(request, pid):
    p = get_object_or_404(Producto, id=pid, activo=True)
    if p.agotado:
        messages.error(request, "Este producto está fuera de stock.")
    else:
        Carrito(request).agregar(p.id)
        messages.success(request, f"{p.nombre} se agregó al carrito.")
    return redirect(request.META.get("HTTP_REFERER", "carrito"))


def quitar(request, pid):
    Carrito(request).quitar(pid)
    return redirect("carrito")


def carrito(request):
    c = Carrito(request)
    prods = Producto.objects.filter(id__in=[int(i) for i in c.data])
    lineas = [(p, c.data[str(p.id)], p.precio * c.data[str(p.id)]) for p in prods]
    return render(request, "FubukiApp/carrito.html", {
        "lineas": lineas, "unidades": c.unidades(), "total": sum(l[2] for l in lineas)})


def checkout(request, agendar=False):
    c = Carrito(request)
    if request.method == "POST":
        datos = {k: request.POST.get(k, "") for k in ("nombre", "email", "telefono", "notas")}
        datos["cumpleanos"] = request.POST.get("cumpleanos") or None
        f = request.POST.get("fecha_entrega")
        fecha = timezone.make_aware(parse_datetime(f)) if f else None
        try:
            pedido = crear_pedido(datos, c.data, fecha)
        except ErrorPedido as e:
            messages.error(request, str(e))
            return redirect(request.path)
        c.vaciar()
        return render(request, "FubukiApp/gracias.html", {"pedido": pedido})
    return render(request, "FubukiApp/checkout.html", {
        "unidades": c.unidades(), "agendar": agendar or c.unidades() > 50})


def pedidos(request):
    if request.method == "POST":
        Sugerencia.objects.create(
            nombre=request.POST["nombre"], contacto=request.POST.get("contacto", ""),
            producto_sugerido=request.POST["producto"], detalle=request.POST.get("detalle", ""))
        messages.success(request, "¡Gracias por tu sugerencia!")
        return redirect("pedidos")
    return render(request, "FubukiApp/pedidos.html")


def resenas(request):
    if request.method == "POST":
        Resena.objects.create(
            producto_id=request.POST["producto"], nombre=request.POST["nombre"],
            estrellas=int(request.POST.get("estrellas", 5)), comentario=request.POST["comentario"])
        messages.success(request, "¡Gracias! Tu reseña se publicará cuando la aprobemos.")
        return redirect("resenas")
    return render(request, "FubukiApp/resenas.html", {
        "productos": Producto.objects.filter(activo=True),
        "resenas": Resena.objects.filter(aprobada=True).order_by("-creado")})
