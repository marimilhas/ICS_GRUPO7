from abc import ABC, abstractmethod
from .excepciones import PagoRechazadoError
from .models import EstadosPago

# --- 1. INTERFACE STRATEGY ---
class IEstrategiaPago(ABC):
    """Interfaz para las diferentes formas de pago."""

    @abstractmethod
    def procesar_pago(self, monto: float, pasarela_pagos):
        """
        Procesa el pago y retorna el estado final de la compra ('Pagada' o 'Pendiente').
        Lanza PagoRechazadoError si el pago es con tarjeta y falla.
        """
        pass

# --- 2. ESTRATEGIAS CONCRETAS ---
class PagoTarjetaStrategy(IEstrategiaPago):
    """Estrategia para pagos con tarjeta (vía Mercado Pago o similar)."""

    def procesar_pago(self, monto: float, pasarela_pagos):
        # Llama al mock/servicio real de la pasarela
        resultado = pasarela_pagos.procesar_pago(monto=monto)

        if resultado:
            return EstadosPago.PAGADO.value # Retorna 'PAG'
        else:
            raise PagoRechazadoError("El pago con tarjeta fue rechazado por la pasarela.")

class PagoEfectivoStrategy(IEstrategiaPago):
    """Estrategia para pagos en efectivo (en boletería)."""

    def procesar_pago(self, monto: float, pasarela_pagos):
        # No hay interacción con la pasarela; solo se registra como pendiente.
        return EstadosPago.PENDIENTE.value # Retorna 'PEN'

# --- 3. CONTEXTO (Simplificado y gestionado por ServicioCompraEntradas) ---
# En este diseño simple, el ServicioCompraEntradas actúa como el Contexto (o el Manager)
# que decide qué Estrategia instanciar y ejecutar.