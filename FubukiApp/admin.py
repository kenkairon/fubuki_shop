from django.contrib import admin
from .models import *


class LineaInline(admin.TabularInline):
    model = LineaPedido
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "es_combo", "activo")
    list_editable = ("precio", "stock", "activo")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "tipo", "estado", "fecha_entrega", "total", "regalo_cumple")
    list_filter = ("tipo", "estado")
    inlines = [LineaInline]


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("producto", "nombre", "estrellas", "aprobada")
    list_editable = ("aprobada",)


admin.site.register([Cliente, Sugerencia])
