import pytest
from datetime import timedelta
from datetime import date
from unittest.mock import MagicMock, Mock
from src.servicio_compra import ServicioCompraEntradas

# Importar las clases y excepciones
from src.modelo import LimiteEntradasExcedidoError, FechaInvalidaError, ParqueCerradoError

# --- FIXTURES (Datos y Mocks para el Aislamiento) ---


@pytest.fixture
def usuario_valido_mock():
    """Retorna un mock que simula un objeto Usuario ya cargado y válido."""
    # En un sistema real, este mock podría tener atributos como email, nombre, etc.
    return Mock(nombre="Juan Pérez", email="juan@example.com", esta_registrado=True)


@pytest.fixture
def datos_compra_validos():
    """Fixture que retorna una base de datos de compra que cumple todas las reglas."""

    # 1. Definir una fecha válida futura (asumimos un miércoles futuro es un día abierto)
    # Usando una fecha fija de ejemplo para que la prueba sea reproducible
    fecha_base = date(2026, 3, 15)

    # 2. Definir una cantidad base válida (5)
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
    """Fixture que retorna mocks de los servicios externos (Capas 3) configurados como 'válidos'."""
    mocks = {
        'pasarela_pagos': MagicMock(),
        'servicio_correo': MagicMock(),
        'servicio_calendario': MagicMock()
    }

    # Aseguramos que las demás validaciones NO interfieran:
    mocks['servicio_calendario'].es_dia_abierto.return_value = True  # La fecha es de parque abierto
    return mocks

@pytest.fixture
def servicio_compra(mocks_infraestructura):
    """
    Esta fixture inicializa y retorna una nueva instancia
    de ServicioDeCompraDeEntradas en cada test.
    """
    return ServicioCompraEntradas(**mocks_infraestructura)

# --- PRUEBA RED: Límite de Entradas ---

def test_comprar_mas_de_diez_entradas_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
        # Prueba que la validación falla con más de 10 entradas.

        # Creamos los datos para la falla, asegurando coherencia entre cantidad y visitantes
        datos_de_falla = datos_compra_validos.copy()
        cantidad_a_fallar = 11
        datos_de_falla["cantidad"] = cantidad_a_fallar

        # Se asegura que la lista de visitantes tenga 11 elementos
        visitante_base = datos_de_falla["visitantes"][0]
        datos_de_falla["visitantes"] = [visitante_base] * cantidad_a_fallar

        with pytest.raises(LimiteEntradasExcedidoError):
            servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

# --- PRUEBA RED: Fecha pasada ---

def test_comprar_entradas_fecha_pasada_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    # Crea una fecha pasada (ej. ayer)
    fecha_pasada = date.today() - timedelta(days=1)

    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = fecha_pasada.isoformat()  # <-- Parámetro que causa el fallo

    # Esperamos que el servicio lance la excepción, pero no lo hará (RED)
    with pytest.raises(FechaInvalidaError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

# --- PRUEBA RED: Fecha Lunes ---

def test_comprar_entradas_fecha_lunes_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    # Encontramos el próximo Lunes
    hoy = date.today()
    dias_hasta_lunes = (0 - hoy.weekday() + 7) % 7
    # Aseguramos que sea futuro, si hoy es Lunes, vamos al próximo
    if dias_hasta_lunes == 0: dias_hasta_lunes = 7
    fecha_lunes = hoy + timedelta(days=dias_hasta_lunes)

    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = fecha_lunes.isoformat()  # <-- Parámetro que causa el fallo

    with pytest.raises(ParqueCerradoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)


"""

def test_validar_parametros_dias_parque_cerrado(sistema):
        # Prueba que la validación falla con una fecha en un día que el parque está cerrado
        fechas_invalidas = [
            date(2025, 12, 25),  
            date(2026, 1, 1),    
            date(2025, 11, 3),  # Un lunes futuro al azar
        ]
        for f in fechas_invalidas:
            with pytest.raises(ValueError, match="En esa fecha el parque se encuentra cerrado"):
                sistema.validar_parametros_compra(fecha=f)


def test_validar_parametros_cantidad_valida_no_lanza_error(sistema):
        # Prueba que la validación pasa con una cantidad correcta.
        sistema.validar_parametros_compra(cantidad=5)

def test_procesar_pago_compra_exitoso(sistema, mocker):
        # Prueba que el cálculo del monto y la llamada de pago son correctos.
        mocker.patch.object(sistema.mp_service, 'procesar_pago', return_value=True)
        pago_exitoso, monto = sistema.procesar_pago_compra(cantidad=3, tipo_pase={"nombre": "VIP", "precio": 10000})
        
        assert pago_exitoso is True
        assert monto == 30000

def test_crear_objeto_compra(sistema):
    # Prueba que el objeto Compra se instancia con los datos correctos.
    datos = {
        "fecha_visita": date.today(), "cantidad_entradas": 2, "edades_visitantes": [30, 35],
        "tipo_pase": {"nombre": "VIP", "precio": 10000}, "forma_pago": "tarjeta", "usuario": {"mail": "test@test.com"}
    }
    
    compra_creada = sistema.crear_objeto_compra(datos, monto_total=20000)
    
    assert isinstance(compra_creada, Compra)
    assert compra_creada.cantidad_entradas == 2
    assert compra_creada.monto_total == 20000
    assert compra_creada.usuario["mail"] == "test@test.com"

def test_comprar_entradas_con_datos_validos_y_pago_tarjeta(sistema):
    # Prueba el flujo completo del método 'comprar_entradas'-> en este caso, una compra válida.
    # Verifica que la compra se cree correctamente y que los servicios
    # externos (pago y email) sean llamados como se espera.
    
    # Mockeamos las funciones externas
    mock_procesar_pago = mocker.patch.object(sistema.mp_service, 'procesar_pago', return_value=True)
    mock_enviar_email = mocker.patch.object(sistema.email_service, 'enviar_confirmacion', return_value=True)
    
    # Precondiciones
    usuario_valido = {"nombre": "Ana", "apellido": "López", "mail": "analopez@gmail.com"}
    fecha_valida = date.today() + timedelta(days=1)
    tipo_pase_valido = {"nombre": "VIP", "precio": 10000}
    forma_pago_valida = "tarjeta"

    compra, confirmacion = sistema.comprar_entradas(
        fecha_visita=fecha_valida,
        cantidad_entradas=2,
        edades_visitantes=[24, 22],
        tipo_pase=tipo_pase_valido,
        forma_pago=forma_pago_valida,
        usuario=usuario_valido
    )

    assert isinstance(compra, Compra)
    assert compra.fecha_visita == fecha_valida
    assert len(compra.entradas) == 2
    assert compra.forma_pago == "tarjeta"
    assert compra.usuario["mail"] == 'analopez@gmail.com'
    assert confirmacion is True
    mock_procesar_pago.assert_called_once_with(monto=20000) # 10000 * 2
    mock_enviar_email.assert_called_once_with(
        mail='analopez@gmail.com',
        compra_details=compra.__dict__
    )
"""