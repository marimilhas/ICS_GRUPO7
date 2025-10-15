
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