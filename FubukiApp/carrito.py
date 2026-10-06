class Carrito:
    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault("carrito", {})

    def agregar(self, pid, cantidad=1):
        self.data[str(pid)] = self.data.get(str(pid), 0) + cantidad
        self.session.modified = True

    def quitar(self, pid):
        self.data.pop(str(pid), None)
        self.session.modified = True

    def vaciar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def unidades(self):
        return sum(self.data.values())


def contador(request):
    return {"carrito_unidades": Carrito(request).unidades()}
