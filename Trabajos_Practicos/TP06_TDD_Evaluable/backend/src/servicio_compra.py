from src.modelo import LimiteEntradasExcedidoError, Usuario

class ServicioCompraEntradas:
    """Clase de la Capa de Lógica de Negocio (Service)."""

    # 1. Constructor: Debe recibir los mismos mocks que se pasan en la fixture 'servicio_compra'
    def __init__(self, pasarela_pagos, servicio_correo, servicio_calendario):
        self.pasarela_pagos = pasarela_pagos
        self.servicio_correo = servicio_correo
        self.servicio_calendario = servicio_calendario

    # 2. Método Principal: Debe recibir la firma de argumentos correcta
    def comprar_entradas(self, usuario: Usuario, cantidad: int, fecha_visita: str, tipo_pago: str, visitantes: list):
        """
        Método a construir. Actualmente, no tiene la lógica de validación de cantidad.
        Esta ausencia es lo que causa el fallo RED esperado en el test.
        """

        # El código simplemente ignora la cantidad excesiva (11) y no lanza la excepción.
        # Esto provoca que el 'pytest.raises(LimiteEntradasExcedidoError)' falle.
        return {"mensaje": "Compra iniciada (Validación de cantidad omitida para el test RED)."}