
class LimiteEntradasExcedidoError(Exception):
    """Lanzada cuando la cantidad de entradas supera el límite de 10."""
    pass


class Usuario:
    # Definición mínima para que el mock funcione sin error
    pass


# Excepciones que usaremos en futuros tests
class UsuarioNoRegistradoError(Exception):
    pass


class ParqueCerradoError(Exception):
    pass


class FechaInvalidaError(Exception):
    pass


class FormaDePagoRequeridaError(Exception):
    pass


class EdadInvalidaError(Exception):
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