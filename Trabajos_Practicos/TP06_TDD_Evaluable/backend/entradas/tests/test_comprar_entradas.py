import pytest
import datetime
from datetime import datetime, date
from datetime import timedelta
from unittest.mock import MagicMock, Mock


from ..excepciones import (
    LimiteEntradasExcedidoError,
    ParqueCerradoError,
    FechaInvalidaError,
    EdadInvalidaError,
    PagoRechazadoError,
    PermissionError,
    TipoPaseInvalidoError,
)
from ..models import Compra, Entrada
from ..servicio_compra import ServicioCompraEntradas
from ..repositories import PaseRepository 
from ..models import Pase, EstadosPago


# --- FIXTURES ---


@pytest.fixture
def usuario_valido_mock(db):
    """
    Crea y retorna un objeto User REAL de Django para la persistencia,
    y le añade el atributo esta_registrado para las validaciones del servicio.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Creamos un usuario real en la DB de test
    user = User.objects.create_user(username='juanperez', email='juan@example.com', password='password123', first_name='Juan',
    last_name='Perez')

    # Añadimos el mock-atributo requerido por tu servicio de validación
    user.nombre = user.username  # Asume que el servicio usa 'nombre'
    user.esta_registrado = True
    return user


@pytest.fixture
def usuario_no_valido_mock(db):
    """
    Crea y retorna un objeto User REAL NO registrado (o con el atributo False).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = User.objects.create_user(username='martinag', email='martina@example.com', password='password123', first_name='Martina',
    last_name='Gonzalez')
    user.nombre = user.username
    user.esta_registrado = False  # Falla la validación inicial
    return user


@pytest.fixture
def datos_compra_validos():
    """Fixture que retorna una base de datos de compra que cumple todas las reglas."""
    fecha_base = datetime(2026, 3, 15, 12, 0, 0)
    visitantes_validos = ([{"edad": 30, "tipo_pase": "Regular"}, {"edad": 10, "tipo_pase": "VIP"}, ] * 2
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
    mocks['pasarela_pagos'].procesar_pago.return_value = True
    mocks['servicio_correo'].enviar_confirmacion.return_value = True
    return mocks


@pytest.fixture
def servicio_compra(mocks_infraestructura, pases_iniciales):
    """Fixture que inicializa y retorna una nueva instancia de ServicioCompraEntradas."""

    # Inyectamos el Repositorio de pases REAL
    pase_repo_real = PaseRepository()

    return ServicioCompraEntradas(**mocks_infraestructura, pase_repository=pase_repo_real)


@pytest.fixture
def pases_iniciales(db):
    """Crea los tipos de pase en la DB de prueba."""

    Pase.objects.update_or_create(
        tipo="Regular",
        defaults={"precio": 5000.00}
    )
    Pase.objects.update_or_create(
        tipo="VIP",
        defaults={"precio": 10000.00}
    )

    # Retornamos los pases válidos para usarlos como referencia
    return ["Regular", "VIP"]


# --- FIXTURES DE FECHAS DINÁMICAS ---

@pytest.fixture
def fecha_habil():
    """Genera una fecha válida: día abierto (no lunes, 25/12, 1/1) y dentro del horario 09–19."""
    fecha = datetime.now() + timedelta(days=1)
    while (
            fecha.weekday() == 0
            or (fecha.day == 25 and fecha.month == 12)
            or (fecha.day == 1 and fecha.month == 1)
    ):
        fecha += timedelta(days=1)
    return fecha.replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def fecha_no_habil():
    """Genera una fecha en lunes (día cerrado)."""
    fecha = datetime.now()
    while fecha.weekday() != 0:
        fecha += timedelta(days=1)
    return fecha.replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def fecha_fuera_de_horario():
    """Genera una fecha abierta pero antes del horario de apertura."""
    fecha = datetime.now() + timedelta(days=1)
    while (
            fecha.weekday() == 0
            or (fecha.day == 25 and fecha.month == 12)
            or (fecha.day == 1 and fecha.month == 1)
    ):
        fecha += timedelta(days=1)
    return fecha.replace(hour=8, minute=59, second=59, microsecond=0)


@pytest.fixture
def fecha_al_abrir(fecha_habil):
    """Genera una fecha válida justo a las 9:00."""
    return fecha_habil.replace(hour=9, minute=0, second=0)


@pytest.fixture
def fecha_durante_dia(fecha_habil):
    """Genera una fecha válida a mitad del horario de apertura."""
    return fecha_habil.replace(hour=14, minute=30, second=0)


@pytest.fixture
def fecha_antes_de_cerrar(fecha_habil):
    """Genera una fecha válida justo antes de cerrar (18:59:59)."""
    return fecha_habil.replace(hour=18, minute=59, second=59)


@pytest.fixture
def fecha_al_cerrar(fecha_habil):
    """Genera una fecha inválida justo a la hora de cierre (19:00:00)."""
    return fecha_habil.replace(hour=19, minute=0, second=0)


@pytest.fixture
def fecha_pasada():
    """Genera una fecha en el pasado."""
    return datetime.now() - timedelta(days=365)


@pytest.fixture
def fecha_futura_valida():
    """Genera una fecha futura válida dentro del horario hábil."""
    fecha = datetime.now() + timedelta(days=30)
    while (
            fecha.weekday() == 0
            or (fecha.day == 25 and fecha.month == 12)
            or (fecha.day == 1 and fecha.month == 1)
    ):
        fecha += timedelta(days=1)
    return fecha.replace(hour=14, minute=0, second=0, microsecond=0)


# ====================================================================
# PRUEBAS DE INTEGRACIÓN
# ====================================================================

def test_comprar_entradas_flujo_completo_tarjeta_exitoso(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """Compra exitosa con tarjeta: verifica creación de entradas y confirmación."""
    mock_pasarela = servicio_compra.pasarela_pagos
    mock_correo = servicio_compra.servicio_correo
    mock_pasarela.procesar_pago.return_value = True
    mock_correo.enviar_confirmacion.return_value = True
    monto_esperado = 32500.00

    compra, entradas_resultado, confirmacion = servicio_compra.comprar_entradas(
        usuario=usuario_valido_mock,
        **datos_compra_validos
    )

    assert confirmacion is True
    assert isinstance(entradas_resultado, list)
    assert all(isinstance(e, Entrada) for e in entradas_resultado)
    assert len(entradas_resultado) == datos_compra_validos["cantidad"]

    mock_pasarela.procesar_pago.assert_called_once_with(monto=monto_esperado)
    mock_correo.enviar_confirmacion.assert_called_once()
    _, kwargs_email = mock_correo.enviar_confirmacion.call_args
    assert kwargs_email.get('mail') == usuario_valido_mock.email


def test_comprar_entradas_sin_forma_pago_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """
    Simula la PRUEBA DE USUARIO #2 (sin forma de pago).
    Verifica que el flujo falla con ValueError.
    """

    datos_sin_pago = datos_compra_validos.copy()
    datos_sin_pago.pop("tipo_pago", None)

    with pytest.raises(ValueError, match="Forma de pago inválida: No especificada"):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_sin_pago)

    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
    servicio_compra.servicio_correo.enviar_confirmacion.assert_not_called()


def test_comprar_entradas_parque_cerrado_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """
    Simula la PRUEBA DE USUARIO #3 (fecha con parque cerrado).
    Verifica que el flujo falla con ParqueCerradoError.
    """
    datos_dia_cerrado = datos_compra_validos.copy()
    fecha_lunes = datetime(2025, 11, 10, 12, 0, 0)  # Lunes
    datos_dia_cerrado["fecha_visita"] = fecha_lunes.isoformat()

    with pytest.raises(ParqueCerradoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_dia_cerrado)

    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
    servicio_compra.servicio_correo.enviar_confirmacion.assert_not_called()


def test_comprar_entradas_cantidad_mayor_a_10_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """
    Simula la PRUEBA DE USUARIO #4 (cantidad > 10).
    Verifica que el flujo falla con LimiteEntradasExcedidoError.
    """
    datos_cantidad_excesiva = datos_compra_validos.copy()
    cantidad_invalida = 11
    visitante_base = datos_cantidad_excesiva["visitantes"][0]
    datos_cantidad_excesiva["cantidad"] = cantidad_invalida
    datos_cantidad_excesiva["visitantes"] = [visitante_base] * cantidad_invalida

    with pytest.raises(LimiteEntradasExcedidoError, match="La cantidad de entradas no puede ser mayor a 10."):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_cantidad_excesiva)

    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
    servicio_compra.servicio_correo.enviar_confirmacion.assert_not_called()


def test_comprar_entradas_flujo_efectivo_exitoso(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """Compra exitosa con efectivo: no se llama a la pasarela."""
    datos_efectivo = datos_compra_validos.copy()
    datos_efectivo["tipo_pago"] = "Efectivo"
    mock_pasarela = servicio_compra.pasarela_pagos
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.return_value = True

    compra, entradas_resultado, confirmacion = servicio_compra.comprar_entradas(
        usuario=usuario_valido_mock,
        **datos_efectivo
    )

    assert confirmacion is True
    assert isinstance(entradas_resultado, list)
    assert all(isinstance(e, Entrada) for e in entradas_resultado)
    mock_pasarela.procesar_pago.assert_not_called()
    mock_correo.enviar_confirmacion.assert_called_once()


def test_comprar_entradas_pago_tarjeta_rechazado_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """
    Verifica que el flujo falla si la pasarela rechaza el pago.
    Asegura que NO se envía email.
    """
    datos_tarjeta = datos_compra_validos.copy()
    datos_tarjeta["tipo_pago"] = "Tarjeta"
    mock_pasarela = servicio_compra.pasarela_pagos
    mock_correo = servicio_compra.servicio_correo
    mock_pasarela.procesar_pago.return_value = False

    with pytest.raises(PagoRechazadoError):
        servicio_compra.comprar_entradas(
            usuario=usuario_valido_mock,
            **datos_tarjeta
        )

    mock_pasarela.procesar_pago.assert_called_once()
    mock_correo.enviar_confirmacion.assert_not_called()


def test_comprar_entradas_falla_envio_email(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """Pago OK pero fallo en envío de email."""
    datos_tarjeta = datos_compra_validos.copy()
    datos_tarjeta["tipo_pago"] = "Tarjeta"
    mock_pasarela = servicio_compra.pasarela_pagos
    mock_correo = servicio_compra.servicio_correo
    mock_pasarela.procesar_pago.return_value = True
    mock_correo.enviar_confirmacion.return_value = False

    compra, entradas_resultado, confirmacion = servicio_compra.comprar_entradas(
        usuario=usuario_valido_mock,
        **datos_tarjeta
    )

    assert confirmacion is False
    assert isinstance(entradas_resultado, list)
    assert all(isinstance(e, Entrada) for e in entradas_resultado)
    mock_pasarela.procesar_pago.assert_called_once()
    mock_correo.enviar_confirmacion.assert_called_once()


def test_comprar_entradas_fecha_pasada_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_valido_mock
):
    """
    Verifica que el flujo falla si la fecha_visita es anterior a hoy.
    """
    datos_fecha_pasada = datos_compra_validos.copy()
    fecha_pasada = date.today() - timedelta(days=1)
    dt_pasado = datetime.combine(fecha_pasada, datetime.min.time().replace(hour=12))
    datos_fecha_pasada["fecha_visita"] = dt_pasado.isoformat()

    with pytest.raises(FechaInvalidaError):
        servicio_compra.comprar_entradas(
            usuario=usuario_valido_mock,
            **datos_fecha_pasada
        )

    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
    servicio_compra.servicio_correo.enviar_confirmacion.assert_not_called()


def test_comprar_entradas_usuario_no_registrado_falla(
        servicio_compra,
        datos_compra_validos,
        usuario_no_valido_mock
):
    """
    Verifica que el flujo falla si el usuario no está registrado.
    """
    with pytest.raises(PermissionError, match="Usuario no registrado"):
        servicio_compra.comprar_entradas(
            usuario=usuario_no_valido_mock,
            **datos_compra_validos
        )

    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
    servicio_compra.servicio_correo.enviar_confirmacion.assert_not_called()


# ====================================================================
# PRUEBAS UNITARIAS
# ====================================================================

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


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE EDADES ---

def test_validar_formato_edades_edad_negativa_falla(servicio_compra):
    """ Falla si alguna edad es negativa. """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": -5, "tipo_pase": "VIP"}
    ]
    with pytest.raises(EdadInvalidaError, match="La edad no puede ser negativa"):
        servicio_compra._validar_formato_edades(visitantes_invalidos)


def test_validar_formato_edades_edad_muy_alta_falla(servicio_compra):
    """ Falla si alguna edad es irrealmente alta (ej. > 120). """
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": 150, "tipo_pase": "VIP"}
    ]
    with pytest.raises(EdadInvalidaError, match="La edad proporcionada parece irreal"):
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


def test_validar_formato_pases_falla_con_tipo_incorrecto_falla(servicio_compra):
    """ Falla si 'tipo_pase' no es un string (ej. un número)."""
    visitantes_invalidos = [
        {"edad": 30, "tipo_pase": 123},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    with pytest.raises(ValueError, match="El 'tipo_pase' debe ser texto"):
        servicio_compra._validar_formato_pases(visitantes_invalidos)


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE VALOR DE PASES ---

def test_validar_valor_pase_invalido_falla(servicio_compra):
    """
    Falla si un 'tipo_pase' es un string válido
    pero no corresponde a un tipo de pase existente (ej. 'Premium').
    """
    visitantes_con_pase_invalido = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": "Premium"}
    ]

    with pytest.raises(ValueError, match="Tipo de pase desconocido"):
        servicio_compra._validar_valores_pases(visitantes_con_pase_invalido)


def test_validar_valor_pase_valido_pasa(servicio_compra):
    """ Pasa si todos los 'tipo_pase' son valores válidos ("Regular", "VIP"). """
    visitantes_validos = [
        {"edad": 30, "tipo_pase": "Regular"},
        {"edad": 10, "tipo_pase": "VIP"}
    ]
    try:
        servicio_compra._validar_valores_pases(visitantes_validos)
    except TipoPaseInvalidoError:
        pytest.fail("La validación de valores de pases no debería haber fallado.")


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FECHA Y HORA DE VISITA ---

def test_validar_fecha_dia_habil_pasa(servicio_compra, fecha_habil):
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_habil)
    except ParqueCerradoError:
        pytest.fail(f"La validación no debería haber fallado en un día hábil: {fecha_habil}")


def test_validar_fecha_falla_en_lunes(servicio_compra, fecha_no_habil):
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_no_habil)


def test_validar_fecha_25_diciembre_falla(servicio_compra):
    año = datetime.now().year
    fecha_navidad = datetime(año, 12, 25, 12, 0, 0)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_navidad)


def test_validar_fecha_1_enero_falla(servicio_compra):
    año = datetime.now().year + 1
    fecha_ano_nuevo = datetime(año, 1, 1, 12, 0, 0)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_ano_nuevo)


def test_validar_fecha_lunes_feriado_falla(servicio_compra):
    # Busca el próximo 1 de enero que caiga lunes
    fecha = datetime.now()
    while not (fecha.day == 1 and fecha.month == 1 and fecha.weekday() == 0):
        fecha += timedelta(days=1)
    fecha = fecha.replace(hour=12)
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha)


def test_validar_horario_antes_de_abrir_falla(servicio_compra, fecha_fuera_de_horario):
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_fuera_de_horario)


def test_validar_horario_al_abrir_pasa(servicio_compra, fecha_al_abrir):
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_al_abrir)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado a la hora de apertura.")


def test_validar_horario_durante_el_dia_pasa(servicio_compra, fecha_durante_dia):
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_durante_dia)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado durante el horario hábil.")


def test_validar_horario_antes_de_cerrar_pasa(servicio_compra, fecha_antes_de_cerrar):
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_antes_de_cerrar)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado justo antes de la hora de cierre.")


def test_validar_horario_al_cerrar_falla(servicio_compra, fecha_al_cerrar):
    with pytest.raises(ParqueCerradoError):
        servicio_compra._validar_fecha_hora_visita(fecha_al_cerrar)


def test_validar_fecha_pasada_falla(servicio_compra, fecha_pasada):
    with pytest.raises(FechaInvalidaError):
        servicio_compra._validar_fecha_hora_visita(fecha_pasada)


def test_validar_fecha_futura_valida_pasa(servicio_compra, fecha_futura_valida):
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_futura_valida)
    except (FechaInvalidaError, ParqueCerradoError) as e:
        pytest.fail(f"La validación falló inesperadamente para una fecha futura válida: {e}")


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


# --- PRUEBAS UNITARIAS: CÁLCULO DE PRECIOS Y MONTOS ---

def test_calcular_precio_menor_3_anos_regular(servicio_compra):
    """Menores de 3 con pase Regular entran gratis."""
    precio = servicio_compra._calcular_precio_entrada(1, "Regular")
    assert precio == 0


def test_calcular_precio_menor_3_anos_vip(servicio_compra):
    """Menores de 3 con pase VIP entran gratis ($0)."""
    precio = servicio_compra._calcular_precio_entrada(1, "VIP")
    assert precio == 0


def test_calcular_precio_menor_10_anos_regular(servicio_compra):
    """Menores de 10 con pase Regular pagan mitad"""
    precio = servicio_compra._calcular_precio_entrada(8, "Regular")
    assert precio == 2500  # 5000 / 2


def test_calcular_precio_menor_10_anos_vip(servicio_compra):
    """Menores de 10 con pase VIP pagan mitad"""
    precio = servicio_compra._calcular_precio_entrada(8, "VIP")
    assert precio == 5000  # 10000 / 2


def test_calcular_precio_mayor_60_anos_regular(servicio_compra):
    """Mayores de 60 con pase Regular pagan mitad"""
    precio = servicio_compra._calcular_precio_entrada(65, "Regular")
    assert precio == 2500  # 5000 / 2


def test_calcular_precio_mayor_60_anos_vip(servicio_compra):
    """Mayores de 60 con pase VIP pagan mitad"""
    precio = servicio_compra._calcular_precio_entrada(65, "VIP")
    assert precio == 5000  # 10000 / 2


def test_calcular_precio_adulto_regular(servicio_compra):
    """Adultos (10-60) con pase Regular pagan precio completo"""
    precio = servicio_compra._calcular_precio_entrada(30, "Regular")
    assert precio == 5000


def test_calcular_precio_adulto_vip(servicio_compra):
    """Adultos (10-60) con pase VIP pagan precio completo"""
    precio = servicio_compra._calcular_precio_entrada(30, "VIP")
    assert precio == 10000


def test_calcular_precio_edad_limite_inferior_menores_3(servicio_compra):
    """0 años (límite inferior) con pase Regular entra gratis ($0)."""
    precio = servicio_compra._calcular_precio_entrada(0, "Regular")
    assert precio == 0


def test_calcular_precio_edad_limite_superior_menores_3(servicio_compra):
    """2 años (límite superior) con pase Regular entra gratis ($0)."""
    precio = servicio_compra._calcular_precio_entrada(2, "Regular")
    assert precio == 0


def test_calcular_precio_edad_limite_inferior_menores_10(servicio_compra):
    """3 años (límite inferior) paga la mitad."""
    precio = servicio_compra._calcular_precio_entrada(3, "Regular")
    assert precio == 2500  # Mitad por ser menor de 10


def test_calcular_precio_edad_limite_superior_menores_10(servicio_compra):
    """9 años (límite superior) paga la mitad."""
    precio = servicio_compra._calcular_precio_entrada(9, "Regular")
    assert precio == 2500


def test_calcular_precio_edad_limite_inferior_adulto(servicio_compra):
    """10 años (límite inferior) paga el total."""
    precio = servicio_compra._calcular_precio_entrada(10, "Regular")
    assert precio == 5000


def test_calcular_precio_edad_limite_superior_adulto(servicio_compra):
    """60 años (límite superior) paga el total."""
    precio = servicio_compra._calcular_precio_entrada(60, "VIP")
    assert precio == 10000


def test_calcular_precio_edad_limite_inferior_tercera_edad(servicio_compra):
    """61 años (límite inferior) paga la mitad."""
    precio = servicio_compra._calcular_precio_entrada(61, "VIP")
    assert precio == 5000


def test_calcular_monto_total_un_solo_visitante(servicio_compra):
    """El monto total para un solo adulto regular es $5000."""
    visitantes = [
        {"edad": 30, "tipo_pase": "Regular"}
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 5000


def test_calcular_monto_total_todos_adultos(servicio_compra):
    """Todos adultos - monto completo"""
    visitantes = [
        {"edad": 25, "tipo_pase": "Regular"},  # 5000
        {"edad": 30, "tipo_pase": "VIP"}  # 10000
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 15000


def test_calcular_monto_total_mixto(servicio_compra):
    """Cálculo de monto con diferentes edades"""
    visitantes = [
        {"edad": 2, "tipo_pase": "Regular"},  # 0
        {"edad": 8, "tipo_pase": "Regular"},  # 2500
        {"edad": 35, "tipo_pase": "VIP"},  # 10000
        {"edad": 65, "tipo_pase": "VIP"}  # 5000
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 17500


def test_calcular_monto_total_todos_menores_3_mixto(servicio_compra):
    """Todos menores de 3 años con distintos tipos de pase - Monto $0."""
    visitantes = [
        {"edad": 1, "tipo_pase": "Regular"},
        {"edad": 2, "tipo_pase": "VIP"}
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 0  # 0 + 0


def test_calcular_monto_total_todos_menores_3_vip(servicio_compra):
    """Todos menores de 3 años con pases VIP - Monto $0."""
    visitantes = [
        {"edad": 1, "tipo_pase": "VIP"},
        {"edad": 2, "tipo_pase": "VIP"}
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 0  # 0 + 0


def test_calcular_monto_total_varios_menores(servicio_compra):
    """Múltiples menores (<3 y <10) con diferentes pases"""
    visitantes = [
        {"edad": 2, "tipo_pase": "Regular"},  # 0 (menor a 3 = 0)
        {"edad": 5, "tipo_pase": "Regular"},  # 2500 (50% de 5000)
        {"edad": 7, "tipo_pase": "VIP"},  # 5000 (50% de 10000)
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 7500


def test_calcular_monto_total_todos_mayores_60_regular(servicio_compra):
    """Todos mayores de 60 con pases Regular - Monto mitad precio completo."""
    visitantes = [
        {"edad": 65, "tipo_pase": "Regular"},
        {"edad": 80, "tipo_pase": "Regular"}
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 5000  # 2500 + 2500


def test_calcular_monto_total_solo_regular(servicio_compra):
    """Grupo donde todos eligen Regular"""
    visitantes = [
        {"edad": 5, "tipo_pase": "Regular"},  # 2500
        {"edad": 30, "tipo_pase": "Regular"},  # 5000
        {"edad": 65, "tipo_pase": "Regular"}  # 2500
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 10000  # 2500 + 5000 + 2500


def test_calcular_monto_total_limites_edad(servicio_compra):
    """Cada límite superior e inferior de las categorías de edad."""
    visitantes = [
        {"edad": 0, "tipo_pase": "Regular"},  # Límite inferior Infante        -> $0
        {"edad": 2, "tipo_pase": "VIP"},  # Límite superior Infante        -> $0
        {"edad": 3, "tipo_pase": "Regular"},  # Límite inferior Menor          -> $2500 (50% de 5k)
        {"edad": 9, "tipo_pase": "VIP"},  # Límite superior Menor          -> $5000 (50% de 10k)
        {"edad": 10, "tipo_pase": "Regular"},  # Límite inferior Adulto         -> $5000 (100% de 5k)
        {"edad": 60, "tipo_pase": "VIP"},  # Límite superior Adulto         -> $10000 (100% de 10k)
        {"edad": 61, "tipo_pase": "Regular"},  # Límite inferior Tercera Edad   -> $2500 (50% de 5k)
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 25000  # 0 + 0 + 2500 + 5000 + 5000 + 10000 + 2500


def test_calcular_monto_total_mezcla_extrema(servicio_compra):
    """Mezcla extrema de edades y tipos de pase"""
    visitantes = [
        {"edad": 1, "tipo_pase": "VIP"},  # 0
        {"edad": 2, "tipo_pase": "Regular"},  # 0
        {"edad": 99, "tipo_pase": "VIP"},  # 5000
        {"edad": 100, "tipo_pase": "Regular"},  # 2500
        {"edad": 35, "tipo_pase": "VIP"},  # 10000
        {"edad": 25, "tipo_pase": "Regular"}  # 5000
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 22500  # 0 + 0 + 5000 + 2500 + 10000 + 5000


def test_calcular_monto_total_familia_mixta(servicio_compra):
    """Familia con diferentes edades y tipos de pase"""
    visitantes = [
        {"edad": 2, "tipo_pase": "VIP"},  # 0 (menor 3)
        {"edad": 5, "tipo_pase": "VIP"},  # 5000 (menor 10)
        {"edad": 8, "tipo_pase": "Regular"},  # 2500 (menor 10)
        {"edad": 35, "tipo_pase": "VIP"},  # 10000 (adulto)
        {"edad": 40, "tipo_pase": "Regular"},  # 5000 (adulto)
        {"edad": 65, "tipo_pase": "VIP"},  # 5000 (mayor 60)
        {"edad": 70, "tipo_pase": "Regular"}  # 2500 (mayor 60)
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 30000  # 0 + 5000 + 2500 + 10000 + 5000 + 5000 + 2500


def test_calcular_monto_total_grupo_jovenes_mixto(servicio_compra):
    """Grupo de jóvenes con mezcla VIP/Regular"""
    visitantes = [
        {"edad": 20, "tipo_pase": "VIP"},  # 10000
        {"edad": 22, "tipo_pase": "Regular"},  # 5000
        {"edad": 25, "tipo_pase": "VIP"},  # 10000
        {"edad": 18, "tipo_pase": "Regular"}  # 5000
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 30000  # 10000 + 5000 + 10000 + 5000


def test_calcular_monto_total_tercera_edad_mixta(servicio_compra):
    """Grupo tercera edad con mezcla VIP/Regular"""
    visitantes = [
        {"edad": 65, "tipo_pase": "VIP"},  # 5000
        {"edad": 68, "tipo_pase": "Regular"},  # 2500
        {"edad": 72, "tipo_pase": "VIP"},  # 5000
        {"edad": 75, "tipo_pase": "Regular"}  # 2500
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 15000  # 5000 + 2500 + 5000 + 2500


def test_calcular_monto_total_familia_numerosa_mixta(servicio_compra):
    """Familia numerosa con múltiples combinaciones"""
    visitantes = [
        {"edad": 1, "tipo_pase": "Regular"},  # 0
        {"edad": 4, "tipo_pase": "VIP"},  # 5000
        {"edad": 6, "tipo_pase": "Regular"},  # 2500
        {"edad": 9, "tipo_pase": "VIP"},  # 5000
        {"edad": 12, "tipo_pase": "Regular"},  # 5000
        {"edad": 15, "tipo_pase": "VIP"},  # 10000
        {"edad": 45, "tipo_pase": "VIP"},  # 10000
        {"edad": 50, "tipo_pase": "Regular"},  # 5000
        {"edad": 67, "tipo_pase": "VIP"},  # 5000
        {"edad": 70, "tipo_pase": "Regular"}  # 2500
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 50000  # Suma de todos


def test_calcular_monto_total_solo_vip(servicio_compra):
    """Grupo donde todos eligen VIP"""
    visitantes = [
        {"edad": 5, "tipo_pase": "VIP"},  # 5000
        {"edad": 30, "tipo_pase": "VIP"},  # 10000
        {"edad": 65, "tipo_pase": "VIP"}  # 5000
    ]
    monto_total = servicio_compra._calcular_monto_total(visitantes)
    assert monto_total == 20000  # 5000 + 10000 + 5000


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMA DE PAGO ---

def test_gestionar_pago_falla_sin_forma_pago_falla(servicio_compra):
    """Falla si tipo_pago es None."""
    monto_ejemplo = 15000.00
    with pytest.raises(ValueError, match="Forma de pago inválida: No especificada"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=None)


def test_gestionar_pago_falla_forma_pago_invalida_falla(servicio_compra):
    """Falla si tipo_pago es un string no reconocido."""
    monto_ejemplo = 15000.00
    tipo_invalido = "Cheque"
    with pytest.raises(ValueError, match=f"Forma de pago inválida: '{tipo_invalido}' no reconocido"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_invalido)


def test_gestionar_pago_forma_pago_efectivo_pasa(servicio_compra):
    """Con 'Efectivo', retorna True y NO llama a la pasarela."""
    monto_ejemplo = 10000.00
    tipo_pago = "Efectivo"

    pago_exitoso = servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    assert pago_exitoso == EstadosPago.PENDIENTE.value
    servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()


def test_gestionar_pago_forma_pago_tarjeta_pasa(servicio_compra):
    """Con 'Tarjeta', llama a pasarela y retorna True si el pago es OK."""
    monto_ejemplo = 20000.00
    tipo_pago = "Tarjeta"
    servicio_compra.pasarela_pagos.procesar_pago.return_value = True

    pago_exitoso = servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    assert pago_exitoso == EstadosPago.PAGADO.value
    servicio_compra.pasarela_pagos.procesar_pago.assert_called_once_with(monto=monto_ejemplo)


def test_gestionar_pago_forma_pago_tarjeta_rechazada_falla(servicio_compra):
    """Con 'Tarjeta', lanza PagoRechazadoError si la pasarela falla."""
    monto_ejemplo = 5000.00
    tipo_pago = "Tarjeta"
    servicio_compra.pasarela_pagos.procesar_pago.return_value = False

    with pytest.raises(PagoRechazadoError, match="El pago con tarjeta fue rechazado"):
        servicio_compra._gestionar_pago(monto_total=monto_ejemplo, tipo_pago=tipo_pago)

    servicio_compra.pasarela_pagos.procesar_pago.assert_called_once_with(monto=monto_ejemplo)


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE ENVÍO DE CONFIRMACIÓN VÍA MAIL ---

def test_enviar_confirmacion_exitoso_llama_servicio_correo(servicio_compra, usuario_valido_mock):
    """ Verifica que se llama al servicio de correo con los argumentos correctos. """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_correo_confirmacion.return_value = True
    compra_mock = MagicMock(spec=Compra)
    compra_mock.id = 123
    compra_mock.monto_total = 17500.00
    compra_mock.__dict__ = {'id': 123, 'monto_total': 17500.00}

    resultado = servicio_compra._enviar_confirmacion(usuario_valido_mock, compra_mock)

    assert resultado is True
    mock_correo.enviar_confirmacion.assert_called_once()
    _, kwargs = mock_correo.enviar_confirmacion.call_args
    assert kwargs.get('mail') == usuario_valido_mock.email
    assert kwargs.get('compra_details') == compra_mock.__dict__


def test_enviar_confirmacion_maneja_fallo_del_servicio_correo(servicio_compra, usuario_valido_mock):
    """ Falla si el servicio de correoindica un fallo."""
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.return_value = False
    compra_mock = MagicMock(spec=Compra)

    resultado = servicio_compra._enviar_confirmacion(usuario_valido_mock, compra_mock)

    assert resultado is False
    mock_correo.enviar_confirmacion.assert_called_once()


def test_enviar_confirmacion_maneja_excepcion_del_servicio_correo(servicio_compra, usuario_valido_mock):
    """ Falla si el servicio de correo lanza una excepción (simulando error de red, etc.). """
    mock_correo = servicio_compra.servicio_correo
    mock_correo.enviar_confirmacion.side_effect = Exception("Fallo de conexión simulado")
    compra_mock = MagicMock(spec=Compra)

    resultado = servicio_compra._enviar_confirmacion(usuario_valido_mock, compra_mock)

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


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMATO DE USUARIO  ---

def test_validar_formato_usuario_valido_pasa(servicio_compra, usuario_valido_mock):
    """ Pasa si el usuario tiene todos los atributos requeridos. """
    try:
        servicio_compra._validar_formato_usuario(usuario_valido_mock)
    except ValueError:
        pytest.fail("La validación de formato de usuario no debería haber fallado.")


def test_validar_formato_usuario_none_falla(servicio_compra):
    """ Falla si el usuario es None. """
    with pytest.raises(ValueError, match="No se proporcionó información del usuario"):
        servicio_compra._validar_formato_usuario(None)


def test_validar_formato_usuario_falta_nombre_falla(servicio_compra):
    """ Falla si falta el atributo 'nombre'. """
    usuario_incompleto = Mock(email="test@test.com", esta_registrado=True, spec=['email', 'esta_registrado'])
    with pytest.raises(ValueError, match="Falta el atributo 'first_name'"):
        servicio_compra._validar_formato_usuario(usuario_incompleto)


def test_validar_formato_usuario_falta_email_falla(servicio_compra):
    """ Falla si falta el atributo 'email'. """
    usuario_incompleto = Mock(first_name="Test", esta_registrado=True, spec=['nombre', 'esta_registrado'])
    with pytest.raises(ValueError, match="Falta el atributo 'email'"):
        servicio_compra._validar_formato_usuario(usuario_incompleto)


def test_validar_formato_usuario_falta_esta_registrado_falla(servicio_compra):
    """ Falla si falta el atributo 'esta_registrado'. """
    usuario_incompleto = Mock(first_name="Test", email="test@test.com", spec=['nombre', 'email'])
    with pytest.raises(ValueError, match="Falta el atributo 'esta_registrado'"):
        servicio_compra._validar_formato_usuario(usuario_incompleto)


def test_validar_formato_usuario_nombre_vacio_falla(servicio_compra):
    """ Falla si el nombre es un string vacío. """
    usuario_invalido = Mock(first_name="", email="test@test.com", esta_registrado=True)
    with pytest.raises(ValueError, match="El atributo 'first_name' no puede estar vacío"):
        servicio_compra._validar_formato_usuario(usuario_invalido)


def test_validar_formato_usuario_email_vacio_falla(servicio_compra):
    """ Falla si el email es un string vacío. """
    usuario_invalido = Mock(first_name="Test", email="", esta_registrado=True)
    with pytest.raises(ValueError, match="El atributo 'email' no puede estar vacío"):
        servicio_compra._validar_formato_usuario(usuario_invalido)


def test_validar_formato_usuario_tipo_incorrecto_falla(servicio_compra):
    """Falla si 'esta_registrado' no es booleano."""
    usuario_invalido = Mock(first_name="Test", email="test@test.com", esta_registrado="True")
    with pytest.raises(ValueError, match="El atributo 'esta_registrado' debe ser de tipo bool"):
        servicio_compra._validar_formato_usuario(usuario_invalido)


# --- PRUEBAS UNITARIAS: VALIDACIÓN DE FORMA DE PAGO ---

def test_validar_forma_pago_valido_pasa(servicio_compra):
    """ Pasa si el tipo de pago es Tarjeta o Efectivo (valores válidos). """
    try:
        servicio_compra._validar_forma_pago("Tarjeta")
        servicio_compra._validar_forma_pago("Efectivo")
    except ValueError:
        pytest.fail("La validación de forma de pago no debería haber fallado con valores válidos.")

def test_validar_forma_pago_none_falla(servicio_compra):
    """ Falla si tipo_pago es None (CdE: Ausencia de valor). """
    with pytest.raises(ValueError, match="Forma de pago inválida: No especificada"):
        servicio_compra._validar_forma_pago(None)

def test_validar_forma_pago_vacio_falla(servicio_compra):
    """ Falla si tipo_pago es string vacío/solo espacios (CdE: Formato inválido). """
    with pytest.raises(ValueError, match="Forma de pago inválida: No especificada"):
        servicio_compra._validar_forma_pago(" ")

def test_validar_forma_pago_invalido_falla(servicio_compra):
    """ Falla si el valor es un string no reconocido (CdE: Valor fuera de rango). """
    with pytest.raises(ValueError, match="Forma de pago inválida: 'Cheque' no reconocido"):
        servicio_compra._validar_forma_pago("Cheque")
