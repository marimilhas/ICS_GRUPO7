# entradas/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import get_user_model  # Necesario para obtener el modelo User
from unittest.mock import Mock  # Necesario si quieres conservar el Mock para visitantes (aunque no usado aquí)

from .servicio_compra import ServicioCompraEntradas
from .repositories import PaseRepository
from .excepciones import LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError, \
    FechaInvalidaError

# Obtener el modelo User activo de Django
User = get_user_model()


# ----------------------------------------------------------------------
# 1. SIMULACIONES DE INFRAESTRUCTURA (Mocks simples para la View) 🎭
# ----------------------------------------------------------------------

class PasarelaPagosSimulada:
    """Simula la pasarela de pagos, siempre aprueba si el monto no es excesivo."""

    # La lógica real de la estrategia de pago asumirá que esta simulación retorna el bool.
    def procesar_pago(self, monto: float) -> bool:
        if monto > 100000:
            print(f"SIMULACIÓN PAGO: [RECHAZADO] Monto: {monto}")
            return False
        print(f"SIMULACIÓN PAGO: [APROBADO] Monto: {monto}")
        return True


class ServicioCorreoSimulado:
    """Simula el servicio de envío de correos."""

    def enviar_confirmacion(self, mail: str, compra_details: dict) -> bool:
        print(f"SIMULACIÓN CORREO: [OK] Confirmación enviada a {mail}")
        return True


class ServicioCalendarioSimulado:
    """Simula la consulta al calendario de días festivos/horarios."""

    def es_dia_abierto(self, fecha) -> bool:
        return True


# ----------------------------------------------------------------------
# 2. FUNCIÓN AUXILIAR PARA OBTENER USUARIO (Resuelve el error de la ForeignKey) 💡
# ----------------------------------------------------------------------

def obtener_usuario_simulado(request):
    """
    Retorna request.user si está autenticado. Si no, crea/obtiene una
    instancia REAL de User de Django para satisfacer la ForeignKey.
    """
    if request.user.is_authenticated:
        return request.user

    # --- SOLUCIÓN AL ValueError: Cannot assign "<Mock>" ---

    # 1. Obtener o crear el usuario de simulación en la DB
    usuario_simulado, creado = User.objects.get_or_create(
        username='simulador_compra',
        defaults={
            'email': 'simulador@parque.com',
            # Es necesario establecer un password si es un usuario real de Django.
            'password': 'password_inseguro_simulacion',
            'is_active': True,
        }
    )

    # 2. Adaptar la instancia real con los atributos que tu Servicio necesita
    # (ya que los mocks se usan en tests, pero aquí adaptamos el objeto real)
    usuario_simulado.esta_registrado = True
    usuario_simulado.nombre = usuario_simulado.username

    return usuario_simulado


# ----------------------------------------------------------------------
# 3. VISTA (Endpoint)
# ----------------------------------------------------------------------

@csrf_exempt
def comprar_entradas_view(request):
    """Endpoint que orquesta la compra de entradas (HTTP POST)."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)

        # 1. Obtener usuario (real o simulado y PERSISTIDO en DB)
        usuario = obtener_usuario_simulado(request)

        cantidad = data.get("cantidad")
        fecha_visita = data.get("fecha_visita")
        tipo_pago = data.get("tipo_pago")
        visitantes = data.get("visitantes", [])

        # 2. Instanciar dependencias inyectando las simulaciones
        servicio_compra = ServicioCompraEntradas(
            pasarela_pagos=PasarelaPagosSimulada(),
            servicio_correo=ServicioCorreoSimulado(),
            servicio_calendario=ServicioCalendarioSimulado(),
            pase_repository=PaseRepository(),  # El Repositorio es real
        )

        # 3. Llamar al método principal del servicio
        entradas, email_enviado = servicio_compra.comprar_entradas(
            usuario=usuario,
            cantidad=cantidad,
            fecha_visita=fecha_visita,
            tipo_pago=tipo_pago,
            visitantes=visitantes
        )

        # 4. Serializar y responder
        entradas_json = [
            {
                "id": getattr(e, 'id', None),
                "tipo_pase": e.pase.tipo,
                "edad_visitante": e.edad_visitante,
                "precio": float(e.precio_calculado),  # Convertir a float para JSON
            }
            for e in entradas
        ]

        return JsonResponse({
            "status": "ok",
            "monto_total": sum(e["precio"] for e in entradas_json),
            "entradas": entradas_json,
            "email_enviado": email_enviado
        }, status=201)

    except (
            LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError,
            FechaInvalidaError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        # En un sistema real, aquí se usaría un logger.
        return JsonResponse({"error": f"Error inesperado: {type(e).__name__} - {str(e)}"}, status=500)