# entradas/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from entradas.servicio_compra import ServicioCompraEntradas
from entradas.repositories import PaseRepository
from entradas.excepciones import LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError, FechaInvalidaError, PermissionError
from unittest.mock import MagicMock
from types import SimpleNamespace
import traceback
from django.contrib.auth.models import User

# Función auxiliar para inicializar el servicio (reutilizado)
def _inicializar_servicio():
    # 1️⃣ Creamos mocks de servicios externos
    mocks_infraestructura = {
        'pasarela_pagos': MagicMock(),
        'servicio_correo': MagicMock(),
        'servicio_calendario': MagicMock(),
    }
    mocks_infraestructura['servicio_calendario'].es_dia_abierto.return_value = True
    mocks_infraestructura['pasarela_pagos'].procesar_pago.return_value = True
    mocks_infraestructura['servicio_correo'].enviar_confirmacion.return_value = True

    # 2️⃣ Inyectamos el repositorio real de pases
    pase_repo_real = PaseRepository()

    # 3️⃣ Inicializamos ServicioCompraEntradas con mocks + repositorio
    try:
        servicio = ServicioCompraEntradas(
            **mocks_infraestructura,
            pase_repository=pase_repo_real
        )
        return servicio
    except Exception as e:
        print("❌ Error al inicializar ServicioCompraEntradas:", e)
        raise Exception(f"Error interno en la inicialización del servicio: {str(e)}")


class ValidarCompraView(APIView):
    """
    NUEVO ENDPOINT: Valida los parámetros de la compra (fecha, cantidad, edades, pases).
    Retorna 200 OK y el monto total si es válido, o 400 Bad Request si falla.
    """
    def post(self, request):
        data = request.data
        print("📥 Datos recibidos para validación:", data)

        # Simulación de obtención de usuario (ajustada para validación)
        usuario_data = data.get('usuario', {})
        usuario = SimpleNamespace(
            first_name=usuario_data.get('nombre', 'Cliente'),
            email=usuario_data.get('email', 'test@example.com'),
            esta_registrado=usuario_data.get('esta_registrado', True)  # Asumimos registrado para validación de negocio
        )
        print("👤 Usuario mockeado para validación:", usuario.email)

        try:
            servicio = _inicializar_servicio()

            # ✅ Validación y cálculo de monto total
            _, monto_total = servicio.validar_parametros_compra(
                usuario=usuario,
                cantidad=data.get('cantidad'),
                fecha_visita=data.get('fecha_visita'),
                visitantes=data.get('visitantes', []),
                tipo_pago=data.get('forma_pago')
            )
            print("✅ Validación de parámetros exitosa. Monto:", monto_total)

            return Response({
                "mensaje": "Parámetros de compra válidos.",
                "monto_total_validado": monto_total
            }, status=status.HTTP_200_OK)

        except (LimiteEntradasExcedidoError, ParqueCerradoError, EdadInvalidaError,
                FechaInvalidaError, PermissionError, ValueError) as e:
            # Errores de negocio y validación
            print("⚠️ Error de negocio en validación:", e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Error inesperado
            print("❌ Error inesperado durante la validación:", e)
            traceback.print_exc()
            return Response({'error': f"Error interno en la validación: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ComprarEntradasView(APIView):
    """
    Endpoint para comprar entradas usando la lógica de ServicioCompraEntradas.
    """

    def post(self, request):
        data = request.data
        print("📥 Datos recibidos:", data)

        # Datos del usuario recibidos en el request
        usuario_data = data.get('usuario', {})
        usuario_email = usuario_data.get('email')
        usuario_nombre = usuario_data.get('nombre', 'Cliente')
        usuario_registrado = usuario_data.get('esta_registrado', True)

        # Buscar o crear un usuario real de Django
        usuario, creado = User.objects.get_or_create(
            username=usuario_email,  # username único obligatorio en Django
            defaults={
                'email': usuario_email,
                'first_name': usuario_nombre,
                # 'last_name' también puede agregarse si querés
            }
        )

        # Guardamos un atributo extra 'esta_registrado' para tu lógica
        # Nota: no es un campo real de User, pero puedes agregarlo dinámicamente
        usuario.esta_registrado = usuario_registrado

        print("👤 Usuario configurado:", usuario, "Creado?", creado)

        # 1️⃣ Creamos mocks de servicios externos
        mocks_infraestructura = {
            'pasarela_pagos': MagicMock(),
            'servicio_correo': MagicMock(),
            'servicio_calendario': MagicMock(),
        }

        # Configuramos retornos simulados
        mocks_infraestructura['servicio_calendario'].es_dia_abierto.return_value = True
        mocks_infraestructura['pasarela_pagos'].procesar_pago.return_value = True
        mocks_infraestructura['servicio_correo'].enviar_confirmacion.return_value = True
        print("🔧 Mocks configurados correctamente")

        # 2️⃣ Inyectamos el repositorio real de pases
        pase_repo_real = PaseRepository()
        print("📚 Repositorio de pases inicializado")

        # 3️⃣ Inicializamos ServicioCompraEntradas con mocks + repositorio
        try:
            servicio = ServicioCompraEntradas(
                **mocks_infraestructura,
                pase_repository=pase_repo_real
            )
            print("✅ ServicioCompraEntradas inicializado")
        except Exception as e:
            print("❌ Error al inicializar ServicioCompraEntradas:", e)
            return Response({'error': f"Error interno en la inicialización: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            compra, entradas, confirmacion = servicio.comprar_entradas(
                usuario=usuario,
                cantidad=data.get('cantidad'),
                fecha_visita=data.get('fecha_visita'),
                visitantes=data.get('visitantes', []),
                tipo_pago=data.get('forma_pago')
            )
            print("✅ Compra realizada correctamente", compra)
            print("📦 Entradas:", entradas)
            print("📧 Confirmación email:", confirmacion)

            # Serialización simplificada (JSON)
            entradas_serializadas = [{
                'id': e.id,
                'pase': e.pase.tipo,
                'edad_visitante': e.edad_visitante,
                'precio_calculado': e.precio_calculado
            } for e in entradas]

            # Objeto de compra que devuelve el backend
            compra_serializada = {
                'id': compra.id,
                'fecha_visita': compra.fecha_visita.strftime("%Y-%m-%d"),
                'cantidad_entradas': len(entradas_serializadas),
                'forma_pago': compra.forma_pago,
                'email': usuario_email,
                'total': compra.monto_total,
                'entradas': entradas_serializadas,
                'nombre': usuario_nombre
            }

            # Respuesta final
            response_data = {
                'compra': compra_serializada,
                'mensajeMail': confirmacion
            }

            print("Response data:", response_data)

            return Response(response_data, status=status.HTTP_201_CREATED)

        except (LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError, FechaInvalidaError, PermissionError, ValueError) as e:
            print("⚠️ Error de negocio:", e)
            traceback.print_exc()  # ← agrega esto
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Error inesperado
            print("❌ Error inesperado:", e)
            traceback.print_exc()  # ← agrega esto
            return Response({'error': f"Error interno en la compra: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
