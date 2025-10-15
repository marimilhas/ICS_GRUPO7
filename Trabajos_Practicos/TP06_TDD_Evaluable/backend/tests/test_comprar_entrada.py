import pytest
from datetime import timedelta
from datetime import date


@pytest.fixture
def sistema():
    return Sistema()

def test_validar_parametros_cantidad_excesiva(sistema):
        # Prueba que la validación falla con más de 10 entradas.
        with pytest.raises(ValueError, match="La cantidad de entradas no puede ser mayor a 10"):
            sistema.validar_parametros_compra(cantidad=11)

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

def test_validar_parametros_visita_pasada(sistema):
        # Prueba que la validación falla con una fecha anterior a la actual, o en la fecha actual pero fuera de hora
        ahora = date.today()

        fechas_invalidas = [
            ahora - timedelta(days=1),   # Ayer
            ahora  # Comprobar al validar la compra si se está en rango horario
        ]

        for f in fechas_invalidas:
            with pytest.raises(ValueError, match="Es una fecha pasada"):
                sistema.validar_parametros_compra(fecha=f, hora=20)

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