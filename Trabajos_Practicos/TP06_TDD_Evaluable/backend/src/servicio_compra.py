from datetime import datetime
from src.exceptions import *
from src.models import *
# from .exceptiones import * 
# from .models import *

class ServicioCompraEntradas:
    """Clase de la Capa de Lógica de Negocio (Service)."""

    # 1. Constructor: Debe recibir los mismos mocks que se pasan en la fixture 'servicio_compra'
    def __init__(self, pasarela_pagos, servicio_correo):
        self.pasarela_pagos = pasarela_pagos
        self.servicio_correo = servicio_correo

    # 2. Método Principal: Debe recibir la firma de argumentos correcta
    def comprar_entradas(self, usuario: Usuario, cantidad: int, fecha_visita: str, tipo_pago: str, visitantes: list):
        """
        Método a construir. Actualmente, no tiene la lógica de validación de cantidad.
        Esta ausencia es lo que causa el fallo RED esperado en el test.
        """

        # El código simplemente ignora la cantidad excesiva (11) y no lanza la excepción.
        # Esto provoca que el 'pytest.raises(LimiteEntradasExcedidoError)' falle.
        return {"mensaje": "Compra iniciada (Validación de cantidad omitida para el test RED)."}
    
    def _calcular_monto_total(self, visitantes: list) -> float:
        """
        Calculará el monto total sumando todos los precios individuales.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación en fase GREEN")

    def _gestionar_pago(self, monto_total: float, tipo_pago: str) -> bool:
        """
        Procesará el pago según el tipo de pago.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación en fase GREEN")
    
    # --- Métodos de Validación de Formato ---

    def _validar_formato_fecha(self, fecha_str: str) -> datetime:
        """
        Valida que el string de fecha tenga formato ISO y lo convierte.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_formato_cantidad(self, cantidad):
        """
        Valida que la cantidad sea un entero.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_formato_edades(self, visitantes: list):
        """
        Valida que las edades sean enteros no negativos.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_formato_pases(self, visitantes: list):
        """
        Valida que cada 'tipo_pase' sea un string no vacío.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_formato_usuario(self, usuario):
        """
        Valida que el objeto usuario tenga la estructura esperada.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    # --- Métodos de Validación de Reglas de Negocio ---

    def _validar_cantidad(self, cantidad: int, visitantes: list):
        """
        Valida cantidad (1-10) y consistencia con lista de visitantes.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_fecha_hora_visita(self, fecha_hora: datetime):
        """
        Valida día (no lunes, no feriado) y horario (9-19).
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_valores_pases(self, visitantes: list):
        """
        Valida que los 'tipo_pase' existan (ej. 'Regular', 'VIP').
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _validar_usuario(self, usuario: Usuario): 
        """
        Valida si el usuario está registrado.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    # --- Métodos de Lógica de Negocio ---

    def _calcular_precio_entrada(self, edad: int, tipo_pase: str) -> float:
        """
        Calcula el precio de UNA entrada según edad y tipo de pase.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _calcular_monto_total(self, visitantes: list) -> float:
        """
        Calcula el monto total sumando precios individuales.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _gestionar_pago(self, monto_total: float, tipo_pago: str) -> bool: # O _procesar_pago
        """
        Procesa el pago según el tipo (llama a pasarela si es Tarjeta).
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    def _enviar_confirmacion(self, usuario: Usuario, compra: Compra) -> bool: 
        """
        Llama al servicio de correo para enviar la confirmación.
        Será implementado en fase GREEN.
        """
        raise NotImplementedError("Método pendiente de implementación")

    # Podrías necesitar un método para crear el objeto Compra al final
    # def _crear_objeto_compra(self, datos_compra, monto_total) -> Compra:
    #     raise NotImplementedError("Método pendiente de implementación")