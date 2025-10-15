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

def test_validar_parametros_cantidad_valida_no_lanza_error(sistema):
        # Prueba que la validación pasa con una cantidad correcta.
        sistema.validar_parametros_compra(cantidad=5)

def test_procesar_pago_compra_exitoso(sistema, mocker):
        # Prueba que el cálculo del monto y la llamada de pago son correctos.
        mocker.patch.object(sistema.mp_service, 'procesar_pago', return_value=True)
        pago_exitoso, monto = sistema.procesar_pago_compra(cantidad=3, tipo_pase={"nombre": "VIP", "precio": 10000})
        
        assert pago_exitoso is True
        assert monto == 3000

def test_crear_objeto_compra(sistema):
    # Prueba que el objeto Compra se instancia con los datos correctos.
    datos = {
        "fecha_visita": date.today(), "cantidad_entradas": 2, "edades_visitantes": [30, 35],
        "tipo_pase": {"nombre": "VIP", "precio": 10000}, "forma_pago": "tarjeta", "usuario": {"mail": "test@test.com"}
    }
    
    compra_creada = sistema.crear_objeto_compra(datos, monto_total=2000)
    
    assert isinstance(compra_creada, Compra)
    assert compra_creada.cantidad_entradas == 2
    assert compra_creada.monto_total == 2000
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