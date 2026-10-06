from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    foto = models.ImageField(upload_to="productos/")
    stock = models.PositiveIntegerField(default=0)
    es_combo = models.BooleanField(default=False)
    incluye = models.ManyToManyField("self", blank=True, symmetrical=False)
    activo = models.BooleanField(default=True)

    @property
    def agotado(self):
        return self.stock == 0

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    cumpleanos = models.DateField(null=True, blank=True)
    compras_completadas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class Pedido(models.Model):
    TIPOS = [("INM", "Compra normal"), ("AGE", "Pedido agendado"), ("ESP", "Pedido especial (+50 u.)")]
    ESTADOS = [("PEN", "Pendiente"), ("CON", "Confirmado"), ("ENT", "Entregado"), ("CAN", "Cancelado")]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="pedidos")
    tipo = models.CharField(max_length=3, choices=TIPOS, default="INM")
    estado = models.CharField(max_length=3, choices=ESTADOS, default="PEN")
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    regalo_cumple = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)


class Sugerencia(models.Model):
    nombre = models.CharField(max_length=120)
    contacto = models.CharField(max_length=120, blank=True)
    producto_sugerido = models.CharField(max_length=200)
    detalle = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)


class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="resenas")
    nombre = models.CharField(max_length=80)
    estrellas = models.PositiveSmallIntegerField(default=5)
    comentario = models.TextField()
    aprobada = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
