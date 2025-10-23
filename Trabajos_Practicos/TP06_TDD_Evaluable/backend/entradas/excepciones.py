class LimiteEntradasExcedidoError(Exception):
    """Lanzada cuando la cantidad de entradas supera el límite de 10."""
    def __init__(self, mensaje="No se pueden comprar más de 10 entradas por transacción"):
        super().__init__(mensaje)


class Usuario:
    # Definición mínima para que el mock funcione sin error
    pass


class UsuarioNoRegistradoError(Exception):
    def __init__(self, mensaje="El usuario debe estar registrado para realizar esta operación"):
        super().__init__(mensaje)


class ParqueCerradoError(Exception):
    """Para cuando en la fecha indicada el parque está cerrado (lunes, navidad o año nuevo)."""
    def __init__(self, mensaje="El parque está cerrado en la fecha seleccionada"):
        super().__init__(mensaje)


class FechaInvalidaError(Exception):
    """Para cuando la fecha indicada es anterior a la actual."""
    def __init__(self, mensaje="La fecha indicada es anterior a la actual"):
        super().__init__(mensaje)


class FormaDePagoRequeridaError(Exception):
    """Para cuando falla una validación de forma de pago"""
    def __init__(self, mensaje="Debe seleccionar una forma de pago válida"):
        super().__init__(mensaje)


class EdadInvalidaError(Exception):
    """Para cuando la edad no cumple el formato, es negativa o muy alta."""
    def __init__(self, mensaje="La edad ingresada no es válida"):
        super().__init__(mensaje)


class PagoRechazadoError(Exception):
    """Para cuando la pasarela de pagos rechaza una transacción."""
    def __init__(self, mensaje="El pago fue rechazado por la pasarela de pagos"):
        super().__init__(mensaje)


class PermissionError(Exception):
    """Para cuando el usuario no tiene permisos"""
    def __init__(self, mensaje="No tiene permisos para realizar esta acción"):
        super().__init__(mensaje)


class TimeoutError(Exception):
    """Para casos de timeout"""
    def __init__(self, mensaje="Tiempo de espera agotado para la operación"):
        super().__init__(mensaje)


class ConnectionError(Exception):
    """Para errores de conexión"""
    def __init__(self, mensaje="Error de conexión con el servicio"):
        super().__init__(mensaje)


class EmailError(Exception):
    """Para errores de envío de email"""
    def __init__(self, mensaje="Error al enviar el correo electrónico"):
        super().__init__(mensaje)


class TipoPaseInvalidoError(Exception):
    """Para tipos de pase inválidos"""
    def __init__(self, mensaje="El tipo de pase seleccionado no es válido"):
        super().__init__(mensaje)