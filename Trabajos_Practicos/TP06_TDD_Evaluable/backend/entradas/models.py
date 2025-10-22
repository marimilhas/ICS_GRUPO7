from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Pase(models.Model):
    tipo = models.CharField(max_length=50, unique=True, help_text="Tipo de pase")
    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Precio del tipo de pase"
    )

    def __str__(self):
        return f"{self.tipo} (${self.precio_base_adulto})"

class EstadosPago(models.TextChoices):
        PENDIENTE = 'PEN', 'Pendiente'
        PAGADO = 'PAG', 'Pagado'
        CANCELADO = 'CAN', 'Cancelado'

class Compra(models.Model):
    class FormasPago(models.TextChoices):
        EFECTIVO = 'EFE', 'Efectivo en Boletería'
        TARJETA = 'TAR', 'Tarjeta (Mercado Pago)'

    usuario = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='compras',
    help_text="Usuario que realizó la compra"
    )

    fecha_compra = models.DateTimeField(default=timezone.now, help_text="Fecha y hora en que se registró la compra")
    fecha_visita = models.DateField(help_text="Fecha elegida por el visitante para ir al parque")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo total calculado de todas las entradas")
    forma_pago = models.CharField(max_length=3, choices=FormasPago.choices, help_text="Método de pago seleccionado")
    estado_pago = models.CharField(max_length=3, choices=EstadosPago.choices, default=EstadosPago.PENDIENTE, help_text="Estado actual del pago")

    def __str__(self):
        return f"Compra #{self.id} - Usuario: {self.usuario.username} - Fecha de visita: {self.fecha_visita}"

    class Meta:
        ordering = ['-fecha_compra']

class Entrada(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='entradas', help_text="Compra a la que pertenece esta entrada")
    pase = models.ForeignKey(Pase, on_delete=models.PROTECT, related_name='entradas_vendidas', help_text="Tipo de pase adquirido")
    edad_visitante = models.PositiveIntegerField(help_text="Edad del visitante")
    precio_calculado = models.DecimalField(max_digits=8, decimal_places=2, help_text="Precio final de esta entrada")

    def __str__(self):
        return f"Entrada para Compra #{self.compra.id} - Pase: {self.pase.tipo} - Edad: {self.edad_visitante}"