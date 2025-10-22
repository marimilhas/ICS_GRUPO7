import pytest
import datetime
from datetime import timedelta
from datetime import datetime
from datetime import date
from unittest.mock import MagicMock, Mock

# Importar las clases y excepciones (asumiendo que existen en el modelo)
from Trabajos_Practicos.TP06_TDD_Evaluable.backend.src.exceptions import LimiteEntradasExcedidoError, FechaInvalidaError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError
from src.servicio_compra import ServicioCompraEntradas

# --- FIXTURES ---

@pytest.fixture
def sistema():
    return Sistema()

@pytest.fixture
def usuario_valido_mock():
    """Retorna un mock que simula un objeto Usuario ya cargado y válido."""
    return Mock(nombre="Juan Pérez", email="juan@example.com", esta_registrado=True)

@pytest.fixture
def usuario_no_valido_mock():
    """Retorna un mock que simula un objeto Usuario ya cargado y válido."""
    return Mock(nombre="Martina González", email="matina@example.com", esta_registrado=False)

@pytest.fixture
def datos_compra_validos():
    """Fixture que retorna una base de datos de compra que cumple todas las reglas."""
    fecha_base = datetime(2026, 3, 15, 12, 0, 0)  # Cambiado a datetime con hora
    visitantes_validos = ([ {"edad": 30, "tipo_pase": "Regular"}, {"edad": 10, "tipo_pase": "VIP"}, ] * 2
                          + [{"edad": 5, "tipo_pase": "Regular"}])  # Total 5 visitantes

    return {
        "cantidad": len(visitantes_validos),  # Cantidad válida: 5
        "fecha_visita": fecha_base.isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": visitantes_validos
    }

@pytest.fixture
def mocks_infraestructura():
    """Fixture que retorna mocks de los servicios externos configurados como 'válidos'."""
    mocks = {
        'pasarela_pagos': MagicMock(),
        'servicio_correo': MagicMock(),
        'servicio_calendario': MagicMock()
    }
    mocks['servicio_calendario'].es_dia_abierto.return_value = True
    return mocks

@pytest.fixture
def servicio_compra(mocks_infraestructura):
    """Fixture que inicializa y retorna una nueva instancia de ServicioCompraEntradas."""
    return ServicioCompraEntradas(**mocks_infraestructura)

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE FECHA Y HORA ---

def test_validar_formato_fecha_formato_correcto_pasa(servicio_compra):
    """ Pasa si el string tiene el formato ISO 8601. """
    fecha_valida = "2025-11-15T10:30:00"
    try:
        fecha = servicio_compra._validar_formato_fecha(fecha_valida)
        assert isinstance(fecha, datetime)
        assert fecha.year == 2025
        assert fecha.hour == 10
    except ValueError:
        pytest.fail("La validación de formato no debería haber fallado.")

def test_validar_formato_fecha_formato_incorrecto_falla(servicio_compra):
    """ Falla si el string no tiene el formato ISO 8601. """
    fecha_str_invalida = "15/11/2025 10:30"
    with pytest.raises(ValueError, match="El formato de la fecha es inválido."):
        servicio_compra._validar_formato_fecha(fecha_str_invalida)

def test_validar_formato_fecha_vacio_falla(servicio_compra):
    """ Falla si el string de fecha está vacío. """
    with pytest.raises(ValueError, match="La fecha de visita no fue proporcionada."):
        servicio_compra._validar_formato_fecha("")

def test_validar_formato_fecha_none_falla(servicio_compra):
    """ Falla si se pasa None en lugar de un string. """
    with pytest.raises(ValueError, match="La fecha de visita no fue proporcionada."):
        servicio_compra._validar_formato_fecha(None)

def test_validar_formato_fecha_tipo_incorrecto_falla(servicio_compra):
    """ Falla si se pasa algo que no es un string. """
    with pytest.raises(ValueError, match="La fecha de visita debe ser un texto"):
        servicio_compra._validar_formato_fecha(12345)

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FECHA Y HORA DE VISITA ---

def test_validar_fecha_dia_habil_pasa(servicio_compra):
    fecha_habil = datetime(2025, 10, 22, 12, 0, 0)  # Miércoles
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_habil)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado en un día hábil.")
        
def test_validar_fecha_falla_en_lunes(servicio_compra):
     fecha_lunes = datetime(2025, 10, 20, 12, 0, 0)  
     with pytest.raises(ParqueCerradoError):
         servicio_compra._validar_fecha_hora_visita(fecha_lunes)
         
def test_validar_fecha_25_diciembre_falla(servicio_compra):
    fecha_navidad = datetime(2025, 12, 25, 12, 0, 0)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_navidad)

def test_validar_fecha_1_enero_falla(servicio_compra):
    fecha_ano_nuevo = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_ano_nuevo)

def test_validar_fecha_lunes_feriado_falla(servicio_compra):
    fecha_especial = datetime(2024, 1, 1, 12, 0, 0) # 1 de Enero de 2024 fue lunes
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_especial)

def test_validar_horario_antes_de_abrir_falla(servicio_compra):
    fecha_valida = datetime(2025, 10, 22, 8, 59, 59)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_visita(fecha_valida)

def test_validar_horario_al_abrir_pasa(servicio_compra):
    fecha_valida = datetime(2025, 10, 22, 9, 0, 0)
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_valida)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado a la hora de apertura.")

def test_validar_horario_durante_el_dia_pasa(servicio_compra):
    fecha_valida = datetime(2025, 10, 22, 14, 30, 0)
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_valida)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado durante el horario hábil.")

def test_validar_horario_antes_de_cerrar_pasa(servicio_compra):
    fecha_valida = datetime(2025, 10, 22, 18, 59, 59)
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_valida)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado justo antes de la hora de cierre.")

def test_validar_horario_al_cerrar_falla(servicio_compra):
    fecha_valida = datetime(2025, 10, 22, 19, 0, 0)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_valida)

def test_validar_fecha_pasada_falla(servicio_compra):
    fecha_pasada = datetime(2024, 10, 22, 12, 0, 0) 

    with pytest.raises(ValueError) as excinfo:
        servicio_compra._validar_fecha_hora_visita(fecha_pasada)

def test_validar_fecha_futura_pasa(servicio_compra):
    fecha_futura = datetime(2026, 10, 22, 12, 0, 0)

    servicio_compra._validar_fecha_hora_visita(fecha_futura)

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE CANTIDAD DE ENTRADAS ---

def test_validar_formato_cantidad_entero_pasa(servicio_compra):
    """ Pasa si la cantidad es un entero. """
    cantidad_valida = 5
    try:
        servicio_compra._validar_formato_cantidad(cantidad_valida)
    except ValueError:
        pytest.fail("La validación de formato no debería haber fallado para un entero.")

def test_validar_formato_cantidad_string_falla(servicio_compra):
    """ Falla si la cantidad es un string. """
    cantidad_invalida = "5"
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser un número entero."):
        servicio_compra._validar_formato_cantidad(cantidad_invalida)

def test_validar_formato_cantidad_float_falla(servicio_compra):
    """ Falla si la cantidad es un float. """
    cantidad_invalida = 5.0
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser un número entero."):
        servicio_compra._validar_formato_cantidad(cantidad_invalida)

def test_validar_formato_cantidad_none_falla(servicio_compra):
    """ Falla si la cantidad es None. """
    cantidad_invalida = None
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser un número entero."):
        servicio_compra._validar_formato_cantidad(cantidad_invalida)

def test_validar_formato_cantidad_otro_tipo_falla(servicio_compra):
    """ Falla si la cantidad es otro tipo (ej. lista)."""
    cantidad_invalida = [5]
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser un número entero"):
        servicio_compra._validar_formato_cantidad(cantidad_invalida)

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE CANTIDAD DE ENTRADAS ---

def test_validar_cantidad_mayor_a_10_falla(servicio_compra):
    """ La validación falla con más de 10 entradas."""
    cantidad_invalida = 11
    visitantes_mock = [{}] * cantidad_invalida
    with pytest.raises(LimiteEntradasExcedidoError, match="La cantidad de entradas no puede ser mayor a 10."):
        servicio_compra._validar_cantidad(cantidad=cantidad_invalida, visitantes=visitantes_mock)

def test_validar_cantidad_cero_falla(servicio_compra):
    """ La validación falla con 0 entradas. """
    cantidad_invalida = 0
    visitantes_mock = []
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser al menos 1."):
        servicio_compra._validar_cantidad(cantidad=cantidad_invalida, visitantes=visitantes_mock)

def test_validar_cantidad_negativa_negativa(servicio_compra):
    """ La validación falla con cantidad negativa de entradas."""
    cantidad_invalida = -1
    visitantes_mock = []
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser al menos 1."):
        servicio_compra._validar_cantidad(cantidad=cantidad_invalida, visitantes=visitantes_mock)

def test_validar_cantidad_no_coincide_con_visitantes_falla(servicio_compra):
    """ La validación falla si la cantidad no coincide con el nro de visitantes."""
    cantidad_valida = 5
    visitantes_incorrectos = [{}] * 3 
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser igual al nro de visitantes."):
        servicio_compra._validar_cantidad(cantidad=cantidad_valida, visitantes=visitantes_incorrectos)

def test_validar_cantidad_datos_validos_pasa(servicio_compra):
    """ La validación pasa si la cantidad está entre 1-10 y coincide con visitantes."""
    cantidad_valida = 7
    visitantes_validos = [{}] * cantidad_valida
    try:
        servicio_compra._validar_cantidad(cantidad=cantidad_valida, visitantes=visitantes_validos)
    except (LimiteEntradasExcedidoError, ValueError):
        pytest.fail("La validación no debería haber fallado con datos válidos.")

def test_validar_cantidad_limite_exacto_10_pasa(servicio_compra):
    """ La validación pasa si la cantidad es exactamente 10 y coincide con visitantes."""
    cantidad_limite = 10
    visitantes_validos = [{}] * cantidad_limite
    try:
        servicio_compra._validar_cantidad(cantidad=cantidad_limite, visitantes=visitantes_validos)
    except (LimiteEntradasExcedidoError, ValueError):
        pytest.fail("La validación no debería haber fallado con la cantidad límite de 10.")
    
# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE EDADES ---

def test_validar_formato_edades_edad_negativa_falla(servicio_compra):
    """ Falla si alguna edad es negativa. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": -5, "tipo_pase": "VIP"} 
    ]
    with pytest.raises(EdadInvalidaError, match="La edad no puede ser negativa"):
        servicio_compra._validar_formato_edades(visitantes_invalidos)

def test_validar_formato_edades_edad_string_falla(servicio_compra):
    """ Falla si alguna edad es un string. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": "veinte", "tipo_pase": "VIP"} 
    ]
    with pytest.raises(EdadInvalidaError, match="La edad debe ser un número entero"):
        servicio_compra._validar_formato_edades(visitantes_invalidos)

def test_validar_formato_edades_edad_float_falla(servicio_compra):
    """ Falla si alguna edad es un número decimal. """
    visitantes_invalidos = [
        {"edad": 30.5, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(EdadInvalidaError, match="La edad debe ser un número entero"):
        servicio_compra._validar_formato_edades(visitantes_invalidos)

def test_validar_formato_edades_edad_none_falla(servicio_compra):
    """ Falla si alguna edad es None. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": None, "tipo_pase": "VIP"} 
    ]
    with pytest.raises(EdadInvalidaError, match="La edad debe ser un número entero"): 
        servicio_compra._validar_formato_edades(visitantes_invalidos)

def test_validar_formato_edades_falta_clave_edad_falla(servicio_compra):
    """ Falla si a un visitante le falta el atributo 'edad'. """
    visitantes_invalidos = [
        {"tipo_pase": "Regular"}, 
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(EdadInvalidaError, match="Falta 'edad' para un visitante"):
        servicio_compra._validar_formato_edades(visitantes_invalidos)

def test_validar_formato_edades_edades_validas_pasa(servicio_compra):
    """ Pasa si todas las edades son enteros positivos. """
    visitantes_validos = [
        {"edad": 25, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": "VIP"},
        {"edad": 5, "tipo_pase": "Regular"}
    ]
    try:
        servicio_compra._validar_formato_edades(visitantes_validos)
    except EdadInvalidaError:
        pytest.fail("La validación de edades no debería haber fallado.")

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE PASES ---    

def test_validar_formato_pases_validos_pasa(servicio_compra):
    """ Pasa si todos los 'tipo_pase' son strings válidos. """
    visitantes_validos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    try:
        servicio_compra._validar_formato_pases(visitantes_validos)
    except ValueError:
        pytest.fail("La validación de formato de pases no debería haber fallado.")

def test_validar_formato_pases_falta_clave_falla(servicio_compra):
    """ Falla si a un visitante le falta la clave 'tipo_pase'."""
    visitantes_invalidos = [
        {"edad": 30}, 
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(ValueError, match="Falta la clave 'tipo_pase'"):
        servicio_compra._validar_formato_pases(visitantes_invalidos)

def test_validar_formato_pases_none_falla(servicio_compra):
    """ Falla si 'tipo_pase' es None. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": None}
    ]
    with pytest.raises(ValueError, match="El 'tipo_pase' debe ser texto"):
        servicio_compra._validar_formato_pases(visitantes_invalidos)

def test_validar_formato_pases_vacio_falla(servicio_compra):
    """ Falla si 'tipo_pase' es un string vacío. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": ""},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(ValueError, match="El 'tipo_pase' no puede estar vacío"):
        servicio_compra._validar_formato_pases(visitantes_invalidos)

def test_validar_formato_pases_falla_con_tipo_incorrecto(servicio_compra):
    """ Falla si 'tipo_pase' no es un string (ej. un número)."""
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": 123},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(ValueError, match="El 'tipo_pase' debe ser texto"):
        servicio_compra._validar_formato_pases(visitantes_invalidos)

# --- PRUEBAS UNITARIAS: CÁLCULO DE PRECIOS Y MONTOS ---

def test_calcular_precio_menor_3_anos_regular(servicio_compra):
    """Prueba RED: menores de 3 con pase Regular entran gratis."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(1, "Regular")
        assert precio == 0
        
def test_calcular_precio_menor_3_anos_vip(servicio_compra):
    """Prueba RED: menores de 3 con pase VIP entran gratis ($0)."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(1, "VIP")
        assert precio == 0        
        
def test_calcular_precio_menor_10_anos_regular(servicio_compra):
    """Prueba RED: menores de 10 con pase Regular pagan mitad"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(8, "Regular")
        assert precio == 2500  # 5000 / 2

def test_calcular_precio_menor_10_anos_vip(servicio_compra):
    """Prueba RED: menores de 10 con pase VIP pagan mitad"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(8, "VIP")
        assert precio == 5000  # 10000 / 2

def test_calcular_precio_mayor_60_anos_regular(servicio_compra):
    """Prueba RED: mayores de 60 con pase Regular pagan mitad"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(65, "Regular")
        assert precio == 2500 # 5000 / 2

def test_calcular_precio_mayor_60_anos_vip(servicio_compra):
    """Prueba RED: mayores de 60 con pase VIP pagan mitad"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(65, "VIP")
        assert precio == 5000  # 10000 / 2

def test_calcular_precio_adulto_regular(servicio_compra):
    """Prueba RED: adultos (10-60) con pase Regular pagan precio completo"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(30, "Regular")
        assert precio == 5000

def test_calcular_precio_adulto_vip(servicio_compra):
    """Prueba RED: adultos (10-60) con pase VIP pagan precio completo"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(30, "VIP")
        assert precio == 10000

def test_calcular_precio_edad_limite_inferior_menores_3(servicio_compra):
    """Prueba RED: 0 años (límite inferior) con pase Regular entra gratis ($0)."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(0, "Regular")
        assert precio == 0

def test_calcular_precio_edad_limite_superior_menores_3(servicio_compra):
    """Prueba RED: 2 años (límite superior) con pase Regular entra gratis ($0)."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(2, "Regular")
        assert precio == 0

def test_calcular_precio_edad_limite_inferior_menores_10(servicio_compra):
    """Prueba RED: 3 años (límite inferior) paga la mitad."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(3, "Regular")
        assert precio == 2500  # Mitad por ser menor de 10

def test_calcular_precio_edad_limite_superior_menores_10(servicio_compra):
    """Prueba RED: 9 años (límite superior) paga la mitad."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(9, "Regular")
        assert precio == 2500

def test_calcular_precio_edad_limite_inferior_adulto(servicio_compra):
    """Prueba RED: 10 años (límite inferior) paga el total."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(10, "Regular")
        assert precio == 5000

def test_calcular_precio_edad_limite_superior_adulto(servicio_compra):
    """Prueba RED: 60 años (límite superior) paga el total."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(60, "VIP")
        assert precio == 10000

def test_calcular_precio_edad_limite_inferior_tercera_edad(servicio_compra):
    """Prueba RED: 61 años (límite inferior) paga la mitad."""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(61, "VIP")
        assert precio == 5000

def test_calcular_monto_total_un_solo_visitante(servicio_compra):
    """Prueba RED: el monto total para un solo adulto regular es $5000."""
    visitantes = [
        {"edad": 30, "tipo_pase": "Regular"}
    ]
    with pytest.raises(AttributeError):
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 5000 

def test_calcular_monto_total_todos_adultos(servicio_compra):
    """Prueba RED: todos adultos - monto completo"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 25, "tipo_pase": "Regular"},  # 5000
            {"edad": 30, "tipo_pase": "VIP"}       # 10000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 15000

def test_calcular_monto_total_mixto(servicio_compra):
    """Prueba RED: cálculo de monto con diferentes edades"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 2, "tipo_pase": "Regular"},   # 0
            {"edad": 8, "tipo_pase": "Regular"},   # 2500
            {"edad": 35, "tipo_pase": "VIP"},      # 10000
            {"edad": 65, "tipo_pase": "VIP"}       # 5000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 17500

def test_calcular_monto_total_todos_menores_3_mixto(servicio_compra):
    """Prueba RED: todos menores de 3 años con distintos tipos de pase - Monto $0."""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 1, "tipo_pase": "Regular"},
            {"edad": 2, "tipo_pase": "VIP"}
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 0 # 0 + 0

def test_calcular_monto_total_todos_menores_3_vip(servicio_compra):
    """Prueba RED: todos menores de 3 años con pases VIP - Monto $0."""
    visitantes = [
        {"edad": 1, "tipo_pase": "VIP"},  
        {"edad": 2, "tipo_pase": "VIP"}   
    ]
    with pytest.raises(AttributeError):
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 0 # 0 + 0

def test_calcular_monto_total_varios_menores(servicio_compra):
    """Prueba RED: múltiples menores (<3 y <10) con diferentes pases"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 2, "tipo_pase": "Regular"},   # 0
            {"edad": 5, "tipo_pase": "Regular"},   # 2500
            {"edad": 7, "tipo_pase": "VIP"},       # 5000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 10000

def test_calcular_monto_total_todos_mayores_60_regular(servicio_compra):
    """Prueba RED: todos mayores de 60 con pases Regular - Monto mitad precio completo."""
    visitantes = [
        {"edad": 65, "tipo_pase": "Regular"},  
        {"edad": 80, "tipo_pase": "Regular"}   
    ]
    with pytest.raises(AttributeError):
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 5000 # 2500 + 2500

def test_calcular_monto_total_solo_regular(servicio_compra):
    """Prueba RED: grupo donde todos eligen Regular"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 5, "tipo_pase": "Regular"},   # 2500
            {"edad": 30, "tipo_pase": "Regular"},  # 5000
            {"edad": 65, "tipo_pase": "Regular"}   # 2500
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 10000  # 2500 + 5000 + 2500

def test_calcular_monto_total_limites_edad(servicio_compra):
    """ Prueba RED: cada límite superior e inferior de las categorías de edad."""
    visitantes = [
        {"edad": 0, "tipo_pase": "Regular"},   # Límite inferior Infante        -> $0
        {"edad": 2, "tipo_pase": "VIP"},       # Límite superior Infante        -> $0
        {"edad": 3, "tipo_pase": "Regular"},   # Límite inferior Menor          -> $2500 (50% de 5k)
        {"edad": 9, "tipo_pase": "VIP"},       # Límite superior Menor          -> $5000 (50% de 10k)
        {"edad": 10, "tipo_pase": "Regular"},  # Límite inferior Adulto         -> $5000 (100% de 5k)
        {"edad": 60, "tipo_pase": "VIP"},      # Límite superior Adulto         -> $10000 (100% de 10k)
        {"edad": 61, "tipo_pase": "Regular"},  # Límite inferior Tercera Edad   -> $2500 (50% de 5k)
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 30000  # 0 + 0 + 2500 + 5000 + 5000 + 10000 + 2500 + 5000

def test_calcular_monto_total_mezcla_extrema(servicio_compra):
    """Prueba RED: mezcla extrema de edades y tipos de pase"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 1, "tipo_pase": "VIP"},       # 0
            {"edad": 2, "tipo_pase": "Regular"},   # 0
            {"edad": 99, "tipo_pase": "VIP"},      # 5000
            {"edad": 100, "tipo_pase": "Regular"}, # 2500
            {"edad": 35, "tipo_pase": "VIP"},      # 10000
            {"edad": 25, "tipo_pase": "Regular"}   # 5000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 22500  # 0 + 0 + 5000 + 2500 + 10000 + 5000

def test_calcular_monto_total_familia_mixta(servicio_compra):
    """Prueba RED: familia con diferentes edades y tipos de pase"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 2, "tipo_pase": "VIP"},       # 0 (menor 3)
            {"edad": 5, "tipo_pase": "VIP"},       # 5000 (menor 10)
            {"edad": 8, "tipo_pase": "Regular"},   # 2500 (menor 10)
            {"edad": 35, "tipo_pase": "VIP"},      # 10000 (adulto)
            {"edad": 40, "tipo_pase": "Regular"},  # 5000 (adulto)
            {"edad": 65, "tipo_pase": "VIP"},      # 5000 (mayor 60)
            {"edad": 70, "tipo_pase": "Regular"}   # 2500 (mayor 60)
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 30000  # 0 + 5000 + 2500 + 10000 + 5000 + 5000 + 2500

def test_calcular_monto_total_grupo_jovenes_mixto(servicio_compra):
    """Prueba RED: grupo de jóvenes con mezcla VIP/Regular"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 20, "tipo_pase": "VIP"},      # 10000
            {"edad": 22, "tipo_pase": "Regular"},  # 5000
            {"edad": 25, "tipo_pase": "VIP"},      # 10000
            {"edad": 18, "tipo_pase": "Regular"}   # 5000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 30000  # 10000 + 5000 + 10000 + 5000

def test_calcular_monto_total_tercera_edad_mixta(servicio_compra):
    """Prueba RED: grupo tercera edad con mezcla VIP/Regular"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 65, "tipo_pase": "VIP"},      # 5000
            {"edad": 68, "tipo_pase": "Regular"},  # 2500
            {"edad": 72, "tipo_pase": "VIP"},      # 5000
            {"edad": 75, "tipo_pase": "Regular"}   # 2500
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 15000  # 5000 + 2500 + 5000 + 2500

def test_calcular_monto_total_familia_numerosa_mixta(servicio_compra):
    """Prueba RED: familia numerosa con múltiples combinaciones"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 1, "tipo_pase": "Regular"},   # 0
            {"edad": 4, "tipo_pase": "VIP"},       # 5000
            {"edad": 6, "tipo_pase": "Regular"},   # 2500
            {"edad": 9, "tipo_pase": "VIP"},       # 5000
            {"edad": 12, "tipo_pase": "Regular"},  # 5000
            {"edad": 15, "tipo_pase": "VIP"},      # 10000
            {"edad": 45, "tipo_pase": "VIP"},      # 10000
            {"edad": 50, "tipo_pase": "Regular"},  # 5000
            {"edad": 67, "tipo_pase": "VIP"},      # 5000
            {"edad": 70, "tipo_pase": "Regular"}   # 2500
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 50000  # Suma de todos

def test_calcular_monto_total_solo_vip(servicio_compra):
    """Prueba RED: grupo donde todos eligen VIP"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 5, "tipo_pase": "VIP"},       # 5000
            {"edad": 30, "tipo_pase": "VIP"},      # 10000
            {"edad": 65, "tipo_pase": "VIP"}       # 5000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 20000  # 5000 + 10000 + 5000

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMA DE PAGO ---

def test_gestionar_pago_falla_sin_forma_pago_falla(servicio_compra):
    """Prueba: Falla si tipo_pago es None."""
    monto_ejemplo = 15000.00
    with pytest.raises(ValueError, match="Forma de pago inválida: No especificada"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=None)

def test_gestionar_pago_falla_forma_pago_invalida_falla(servicio_compra):
    """Prueba: Falla si tipo_pago es un string no reconocido."""
    monto_ejemplo = 15000.00
    tipo_invalido = "Cheque"
    with pytest.raises(ValueError, match=f"Forma de pago inválida: '{tipo_invalido}' no reconocido"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_invalido)

def test_gestionar_pago_forma_pago_efectivo_pasa(servicio_compra):
    """Prueba: Con 'Efectivo', retorna True y NO llama a la pasarela."""
    monto_ejemplo = 10000.00
    tipo_pago = "Efectivo"

    pago_exitoso = servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    assert pago_exitoso is True
    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()

def test_gestionar_pago_forma_pago_tarjeta_pasa(servicio_compra):
    """Prueba: Con 'Tarjeta', llama a pasarela y retorna True si el pago es OK."""
    monto_ejemplo = 20000.00
    tipo_pago = "Tarjeta"
    servicio_compra.pasarela_pagos.procesar_pago.return_value = True

    pago_exitoso = servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    assert pago_exitoso is True
    servicio_compra.pasarela_pagos.procesar_pago.assert_called_once_with(monto=monto_ejemplo)

def test_gestionar_pago_forma_pago_tarjeta_rechazada_falla(servicio_compra):
    """Prueba: Con 'Tarjeta', lanza PagoRechazadoError si la pasarela falla."""
    monto_ejemplo = 5000.00
    tipo_pago = "Tarjeta"
    servicio_compra.pasarela_pagos.procesar_pago.return_value = False

    with pytest.raises(PagoRechazadoError, match="El pago fue rechazado"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    servicio_compra.pasarela_pagos.procesar_pago.assert_called_once_with(monto=monto_ejemplo)

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE ENVÍO DE CONFIRMACIÓN VÍA MAIL ---

def test_enviar_confirmacion_datos_validos_pasa(servicio_compra, usuario_valido_mock):
    """ Verifica que se llama al servicio de correo con los argumentos correctos."""
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_correo_confirmacion.return_value = True

    compra_mock = MagicMock(spec=Compra)
    compra_mock.id = 123
    compra_mock.monto_total = 17500.00
    
    resultado = servicio_compra._enviar_confirmacion(usuario_valido_mock, compra_mock)

    assert resultado is True
    mock_correo.enviar_correo_confirmacion.assert_called_once()
    _, kwargs = mock_correo.enviar_confirmacion.call_args
    assert kwargs.get('mail') == usuario_valido_mock.email
    assert kwargs.get('compra_details') == compra_mock.__dict__

def test_enviar_confirmacion_maneja_fallo_del_servicio_correo(servicio_compra, usuario_valido_mock): # 
    """ Verifica que el método devuelve False si el servicio de correo indica un fallo. """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.return_value = False
    
    compra_mock = MagicMock(spec=Compra)

    resultado = servicio_compra._enviar_notificacion(usuario_valido_mock, compra_mock)

    assert resultado is False
    mock_correo.enviar_confirmacion.assert_called_once()

def test_enviar_notificacion_maneja_excepcion_del_servicio(servicio_compra, usuario_valido_mock): 
     """Verifica cómo se maneja una excepción, usando el usuario de la fixture."""
     mock_correo = servicio_compra.servicio_correo
     mock_correo.enviar_confirmacion.side_effect = EmailError("Fallo simulado")

     compra_mock = MagicMock(spec=Compra)

     with pytest.raises(EmailError, match="Fallo simulado"):
         servicio_compra._enviar_notificacion(usuario_valido_mock, compra_mock) 

     mock_correo.enviar_confirmacion.assert_called_once()

def test_enviar_confirmacion_exitoso(servicio_compra):
    """ Verifica que se llama al servicio de correo con los datos correctos. """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.return_value = True 
    email_destino = "juan@example.com"
    compra_mock = MagicMock(spec=Compra) 
    compra_mock.id = 123
    compra_mock.__dict__ = {'id': 123, 'monto': 100} 

    resultado = servicio_compra._enviar_confirmacion(email_destino, compra_mock)

    assert resultado is True
    mock_correo.enviar_confirmacion.assert_called_once()
    _, kwargs = mock_correo.enviar_confirmacion.call_args
    assert kwargs.get('mail') == email_destino
    assert kwargs.get('compra_details') == compra_mock.__dict__

def test_enviar_confirmacion_maneja_fallo_del_servicio_correo(servicio_compra):
    """ Verifica que el método devuelve False si el servicio de correo indica un fallo. """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.return_value = False
    email_destino = "test@fail.com"
    compra_mock = MagicMock(spec=Compra)

    resultado = servicio_compra._enviar_confirmacion(email_destino, compra_mock)

    assert resultado is False
    mock_correo.enviar_confirmacion.assert_called_once()

def test_enviar_confirmacion_maneja_excepcion_del_servicio_correo(servicio_compra):
    """ Verifica que el método devuelve False si el servicio de correo lanza una excepción (ej: error de red). """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.side_effect = Exception("Fallo simulado")
    email_destino = "error@test.com"
    compra_mock = MagicMock(spec=Compra)

    resultado = servicio_compra._enviar_confirmacion(email_destino, compra_mock)

    assert resultado is False
    mock_correo.enviar_confirmacion.assert_called_once()

# --- PRUEBAS UNITARIAS: VALIDACIÓN DE USUARIO REGISTRADO ---

def test_validar_usuario_no_registrado_falla(servicio_compra, usuario_no_valido_mock):
    """ Falla si un usuario no registrado intenta comprar entradas. """
    with pytest.raises(PermissionError, match="Usuario no registrado"):
        servicio_compra._validar_usuario(usuario_no_valido_mock)

def test_validar_usuario_registrado_pasa(servicio_compra, usuario_valido_mock): 
    """ Pasa si un usuario registrado intenta comprar entradas. """
    try:
        servicio_compra._validar_usuario(usuario_valido_mock)
    except PermissionError:
        pytest.fail("La validación no debería haber fallado para un usuario registrado.")

# DEJO LA ALTERNATIVA POR SI NO SE PUEDE SIMULAR EL OBJETO USUARIO EN EL FRONTEND

# def test_validar_usuario_no_registrado_falla(servicio_compra):
#     """ Falla si un usuario no registrado intenta comprar entradas."""
#     email_no_registrado = "otro@email.com"

#     with pytest.raises(PermissionError, match="Usuario no registrado"):
#         servicio_compra._validar_usuario(email_no_registrado)

# def test_validar_usuario_registrado_pasa(servicio_compra):
#     """ Pasa si un usuario registrado intenta comprar entradas."""
#     email_registrado = "TestUser@Example.com"
#     try:
#         servicio_compra._validar_usuario(email_registrado)
#     except PermissionError:
#         pytest.fail("La validación no debería haber fallado para el email registrado.")
        
# -- PRUEBAS RED: Validaciones de estructura y datos ---

def test_comprar_entradas_edad_negativa_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: edad negativa debe fallar"""
    datos_invalidos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": -5, "tipo_pase": "Regular"}]
    }
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_invalidos)

def test_comprar_entradas_edad_muy_alta_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: edad muy alta (mayor a 150) debe fallar"""
    datos_invalidos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": 200, "tipo_pase": "Regular"}]
    }
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_invalidos)

def test_comprar_entradas_tipo_pase_invalido_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: tipo de pase inválido debe fallar"""
    datos_invalidos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": 25, "tipo_pase": "Premium"}]  # Tipo inválido
    }
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_invalidos)

def test_comprar_entradas_datos_visitante_incompletos_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: datos de visitante incompletos debe fallar"""
    datos_incompletos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": 25}]  # Falta tipo_pase
    }
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_incompletos)

def test_comprar_entradas_edad_string_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: edad como string debe fallar"""
    datos_invalidos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": "veinticinco", "tipo_pase": "Regular"}]  # Edad como string
    }
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_invalidos)

def test_comprar_entradas_tipo_pase_null_falla(servicio_compra, usuario_valido_mock):
    """Prueba RED: tipo pase null debe fallar"""
    datos_invalidos = {
        "cantidad": 1,
        "fecha_visita": date.today().isoformat(),
        "tipo_pago": "Tarjeta",
        "visitantes": [{"edad": 25, "tipo_pase": None}]
    }
        
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_invalidos)

# --- PRUEBAS RED: Validación de Formato Email ---

def test_comprar_entradas_email_usuario_invalido_falla(servicio_compra, datos_compra_validos):
    """Prueba RED: email de usuario inválido debe fallar"""
    usuario_email_invalido = Mock(esta_registrado=True, email="email_invalido")
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_email_invalido, **datos_compra_validos)

def test_comprar_entradas_email_usuario_vacio_falla(servicio_compra, datos_compra_validos):
    """Prueba RED: email de usuario vacío debe fallar"""
    usuario_email_vacio = Mock(esta_registrado=True, email="")
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_email_vacio, **datos_compra_validos)

# --- PRUEBAS RED: Proceso de Compra Completo ----------------------------------------------

def test_comprar_entradas_proceso_completo_exitoso(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: proceso completo de compra exitoso"""
    with pytest.raises(AttributeError):
        # Mockear todas las dependencias externas
        servicio_compra.pasarela_pagos.procesar_pago = MagicMock(return_value=True)
        servicio_compra.servicio_correo.enviar_confirmacion = MagicMock(return_value=True)
        servicio_compra.servicio_calendario.es_dia_abierto.return_value = True
        
        compra = servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_compra_validos)