
class LimiteEntradasExcedidoError(Exception):
    """Lanzada cuando la cantidad de entradas supera el límite de 10."""
    pass


class Usuario:
    # Definición mínima para que el mock funcione sin error
    pass


class UsuarioNoRegistradoError(Exception):
    pass


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
    pass


class EdadInvalidaError(Exception):
    """Para cuando la edad no cumple el formato, es negativa o muy alta."""
    pass


class PagoRechazadoError(Exception):
    """Para cuando la pasarela de pagos rechaza una transacción."""
    pass


class PermissionError(Exception):
    """Para cuando el usuario no tiene permisos"""
    pass


class TimeoutError(Exception):
    """Para casos de timeout"""
    pass


class ConnectionError(Exception):
    """Para errores de conexión"""
    pass


class EmailError(Exception):
    """Para errores de conexión"""
    pass


class TipoPaseInvalidoError(Exception):
    """Para errores de conexión"""
    pass
