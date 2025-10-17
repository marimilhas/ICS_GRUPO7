import pytest
from datetime import timedelta
from datetime import date
from unittest.mock import MagicMock, Mock
from src.servicio_compra import ServicioCompraEntradas
from src.modelo import LimiteEntradasExcedidoError, FechaInvalidaError, ParqueCerradoError

# ====================================================================
#   FIXTURES: Datos y Mocks para el Aislamiento
# ====================================================================
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

# ========================================================================
#   PRUEBAS: Pruebas Unitarias y de Integración para la Lógica de Compra
# ========================================================================

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

# --- PRUEBAS RED: Cálculo de Montos ---
# agustina, agustin, jime 

def test_calcular_precio_adulto_regular(servicio_compra):
    """Prueba RED: adulto (30 años) con pase Regular paga precio completo"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(30, "Regular")
        assert precio == 5000

def test_calcular_precio_adulto_vip(servicio_compra):
    """Prueba RED: adulto (30 años) con pase VIP paga precio completo"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(30, "VIP")
        assert precio == 10000

def test_calcular_monto_total_todos_adultos(servicio_compra):
    """Prueba RED: todos adultos - monto completo"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 25, "tipo_pase": "Regular"},  # 5000
            {"edad": 30, "tipo_pase": "VIP"}       # 10000
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total==15000

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

def test_calcular_monto_total_todos_gratis(servicio_compra):
    """Prueba RED: todos menores de 3 años - monto 0"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 1, "tipo_pase": "Regular"},
            {"edad": 2, "tipo_pase": "VIP"}
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 0

def test_calcular_monto_total_varios_menores(servicio_compra):
    """Prueba RED: múltiples menores con diferentes pases"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 2, "tipo_pase": "Regular"},   # 0
            {"edad": 5, "tipo_pase": "Regular"},   # 2500
            {"edad": 7, "tipo_pase": "VIP"},       # 5000
            {"edad": 70, "tipo_pase": "Regular"}   # 2500
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 10000

# --- PRUEBAS UNITARIAS: Validación de Fecha y Hora ---

def test_validar_fecha_dia_habil_pasa(servicio_compra):
    fecha_habil = datetime(2025, 10, 22, 12, 0, 0)  # Miércoles
    try:
        servicio_compra._validar_fecha_hora_visita(fecha_habil)
    except ParqueCerradoError:
        pytest.fail("La validación no debería haber fallado en un día hábil.")

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

# LO DEJO COMENTADO POR LAS DUDAS, PQ YA LO HIZO JULI EN REALIDAD
# def test_validar_fecha_falla_en_lunes(servicio_compra):
#     fecha_lunes = datetime(2025, 10, 20, 12, 0, 0)  
#     with pytest.raises(ParqueCerradoError):
#         servicio_compra._validar_fecha_hora_visita(fecha_lunes)
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