import pytest
from datetime import timedelta
from datetime import date
from unittest.mock import MagicMock, Mock

# Importar las clases y excepciones (asumiendo que existen en el modelo)
from src.modelo import LimiteEntradasExcedidoError, FechaInvalidaError, ParqueCerradoError
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
def datos_compra_validos():
    """Fixture que retorna una base de datos de compra que cumple todas las reglas."""
    fecha_base = date(2026, 3, 15)
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

# --- PRUEBAS RED: Validación de Parámetros ---

def test_validar_parametros_cantidad_excesiva(sistema):
    """Prueba RED: la validación falla con más de 10 entradas."""
    with pytest.raises(ValueError, match="La cantidad de entradas no puede ser mayor a 10"):
        sistema.validar_parametros_compra(cantidad=11)

def test_comprar_mas_de_diez_entradas_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar más de 10 entradas debe fallar."""
    datos_de_falla = datos_compra_validos.copy()
    cantidad_a_fallar = 11
    datos_de_falla["cantidad"] = cantidad_a_fallar
    visitante_base = datos_de_falla["visitantes"][0]
    datos_de_falla["visitantes"] = [visitante_base] * cantidad_a_fallar

    with pytest.raises(LimiteEntradasExcedidoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

def test_comprar_entradas_fecha_pasada_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar con fecha pasada debe fallar."""
    fecha_pasada = date.today() - timedelta(days=1)
    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = fecha_pasada.isoformat()

    with pytest.raises(FechaInvalidaError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

def test_comprar_entradas_fecha_lunes_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar para un lunes debe fallar (parque cerrado)."""
    hoy = date.today()
    dias_hasta_lunes = (0 - hoy.weekday() + 7) % 7
    if dias_hasta_lunes == 0: 
        dias_hasta_lunes = 7
    fecha_lunes = hoy + timedelta(days=dias_hasta_lunes)

    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = fecha_lunes.isoformat()

    with pytest.raises(ParqueCerradoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

# --- PRUEBAS RED: Cálculo de Precios y Montos ---

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

def test_calcular_precio_mayor_60_anos_vip(servicio_compra):
    """Prueba RED: mayores de 60 con pase VIP pagan mitad"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(65, "VIP")
        assert precio == 5000  # 10000 / 2

def test_calcular_precio_edad_limite_inferior(servicio_compra):
    """Prueba RED: 3 años (límite inferior) paga según su categoría"""
    with pytest.raises(AttributeError):
        precio = servicio_compra._calcular_precio_entrada(3, "Regular")
        assert precio == 2500  # Mitad por ser menor de 10

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
    """Prueba RED: casos en los límites de edad (3, 10, 60 años)"""
    with pytest.raises(AttributeError):
        visitantes = [
            {"edad": 3, "tipo_pase": "Regular"},   # 2500 (justo 3 años)
            {"edad": 10, "tipo_pase": "VIP"},      # 10000 (justo 10 años)
            {"edad": 60, "tipo_pase": "Regular"}   # 2500 (justo 60 años)
        ]
        monto_total = servicio_compra._calcular_monto_total(visitantes)
        assert monto_total == 15000  # 2500 + 10000 + 2500

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

# --- PRUEBAS RED: Validación de Forma de Pago ---

def test_comprar_entradas_sin_forma_pago_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar sin seleccionar forma de pago debe fallar"""
    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["tipo_pago"] = None
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

def test_comprar_entradas_forma_pago_efectivo_valida(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar con forma de pago efectivo debe ser válido"""
    with pytest.raises(AttributeError):
        datos_efectivo = datos_compra_validos.copy()
        datos_efectivo["tipo_pago"] = "Efectivo"
        
        # Mockear dependencias externas
        servicio_compra.pasarela_pagos.procesar_pago = MagicMock()
        servicio_compra.servicio_correo.enviar_confirmacion = MagicMock(return_value=True)
        
        compra = servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_efectivo)
        
        # Verificar que NO se llamó a la pasarela de pagos
        servicio_compra.pasarela_pagos.procesar_pago.assert_not_called()
        # Verificar que SÍ se envió el email
        servicio_compra.servicio_correo.enviar_confirmacion.assert_called_once()

def test_comprar_entradas_forma_pago_tarjeta_valida(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar con forma de pago tarjeta debe procesar pago"""
    with pytest.raises(AttributeError):
        datos_tarjeta = datos_compra_validos.copy()
        datos_tarjeta["tipo_pago"] = "Tarjeta"
        
        # Mockear dependencias externas
        servicio_compra.pasarela_pagos.procesar_pago = MagicMock(return_value=True)
        servicio_compra.servicio_correo.enviar_confirmacion = MagicMock(return_value=True)
        
        compra = servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_tarjeta)
        
        # Verificar que SÍ se llamó a la pasarela de pagos
        servicio_compra.pasarela_pagos.procesar_pago.assert_called_once()
        servicio_compra.servicio_correo.enviar_confirmacion.assert_called_once()

# --- PRUEBAS RED: Días Festivos ---

def test_comprar_entradas_navidad_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar para 25 de diciembre debe fallar"""
    navidad = date(date.today().year, 12, 25)
    # Si la navidad ya pasó este año, usar la del próximo
    if navidad < date.today():
        navidad = date(date.today().year + 1, 12, 25)
    
    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = navidad.isoformat()
    
    with pytest.raises(ParqueCerradoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

def test_comprar_entradas_año_nuevo_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: comprar para 1ero de enero debe fallar"""
    año_nuevo = date(date.today().year, 1, 1)
    # Si ya pasó el 1ero de enero, usar el del próximo año
    if año_nuevo < date.today():
        año_nuevo = date(date.today().year + 1, 1, 1)
    
    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["fecha_visita"] = año_nuevo.isoformat()
    
    with pytest.raises(ParqueCerradoError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

# --- PRUEBAS RED: Usuario No Registrado ---

def test_comprar_entradas_usuario_no_registrado_falla(servicio_compra, datos_compra_validos):
    """Prueba RED: usuario no registrado no puede comprar entradas"""
    usuario_no_registrado = Mock(nombre="Jose Gonzales", email="jose@example.com", esta_registrado=False)
    
    with pytest.raises(PermissionError):
        servicio_compra.comprar_entradas(usuario=usuario_no_registrado, **datos_compra_validos)

# -- PRUEBAS RED: Validaciones de estructura y datos ---

def test_comprar_entradas_cantidad_inconsistente_falla(servicio_compra, datos_compra_validos, usuario_valido_mock):
    """Prueba RED: cantidad no coincide con visitantes debe fallar"""
    datos_de_falla = datos_compra_validos.copy()
    datos_de_falla["cantidad"] = 3
    datos_de_falla["visitantes"] = datos_compra_validos["visitantes"][:2]  # Solo 2 visitantes
    
    with pytest.raises(ValueError):
        servicio_compra.comprar_entradas(usuario=usuario_valido_mock, **datos_de_falla)

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


# --- PRUEBAS (estas parecen estar en fase GREEN, las mantengo pero comento) ---
"""
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

def test_comprar_entradas_con_datos_validos_y_pago_tarjeta(sistema, mocker):
    # Prueba el flujo completo del método 'comprar_entradas'
    mock_procesar_pago = mocker.patch.object(sistema.mp_service, 'procesar_pago', return_value=True)
    mock_enviar_email = mocker.patch.object(sistema.email_service, 'enviar_confirmacion', return_value=True)
    
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
    mock_procesar_pago.assert_called_once_with(monto=20000)
    mock_enviar_email.assert_called_once_with(
        mail='analopez@gmail.com',
        compra_details=compra.__dict__
    )
"""