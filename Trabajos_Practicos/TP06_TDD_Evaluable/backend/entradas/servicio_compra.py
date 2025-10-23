# servicio_compra.py

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .excepciones import LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError, \
    FechaInvalidaError, PermissionError

from .repositories import PaseRepository
from .estrategias_pago import PagoEfectivoStrategy, PagoTarjetaStrategy, IEstrategiaPago
from .models import Compra, Entrada


class ServicioCompraEntradas:
    """Clase de la Capa de Lógica de Negocio (Service)."""

    def __init__(self, pasarela_pagos, servicio_correo, servicio_calendario, pase_repository: PaseRepository):
        self.pasarela_pagos = pasarela_pagos
        self.servicio_correo = servicio_correo
        self.servicio_calendario = servicio_calendario
        self.pase_repository = pase_repository  # <-- Nueva dependencia inyectada

    def validar_parametros_compra(self, usuario: User, cantidad: int, fecha_visita: str, visitantes: list,
                                  tipo_pago: str = None):
        """
        Ejecuta todas las validaciones de negocio sin modificar el estado de la aplicación.
        Retorna True si la validación es exitosa, lanza excepción en caso contrario.
        """
        # 1. Validaciones de Formato y Lógica
        self._validar_formato_usuario(usuario)
        self._validar_usuario(usuario)
        self._validar_formato_cantidad(cantidad)
        self._validar_cantidad(cantidad, visitantes)

        fecha_dt = self._validar_formato_fecha(fecha_visita)

        self._validar_fecha_hora_visita(fecha_dt)

        self._validar_formato_edades(visitantes)
        self._validar_formato_pases(visitantes)
        self._validar_valores_pases(visitantes)

        self._validar_forma_pago(tipo_pago)

        # Opcional, pero útil para tener el total:
        monto_total = self._calcular_monto_total(visitantes)

        # ✅ Retornar tupla
        return True, monto_total

    # 1. Método Principal (Debe fallar para los tests de integración)
    def comprar_entradas(self, usuario: User, cantidad: int, fecha_visita: str, visitantes: list,
                         tipo_pago: str = None):
        """
        Método principal que orquesta la compra.
        Debe fallar en la Fase RED.
        """
        # 1. Validaciones de Formato y Lógica
        # Las validaciones de usuario, cantidad, fechas, edad, y pases (valores)
        # deben ejecutarse en este orden para fallar rápido.
        self._validar_formato_usuario(usuario)
        self._validar_usuario(usuario)
        self._validar_formato_cantidad(cantidad)
        self._validar_cantidad(cantidad, visitantes)

        fecha_dt = self._validar_formato_fecha(fecha_visita)

        self._validar_fecha_hora_visita(fecha_dt)

        self._validar_formato_edades(visitantes)
        self._validar_formato_pases(visitantes)
        self._validar_valores_pases(visitantes)

        forma_pago_codigo = self._validar_forma_pago(tipo_pago)

        # 2. Cálculo del Monto
        monto_total = self._calcular_monto_total(visitantes)

        # 3. Gestión del Pago (Patrón Strategy)
        # Lanza PagoRechazadoError si el pago con tarjeta falla
        estado_compra = self._gestionar_pago(monto_total, tipo_pago)

        # 4. Creación y Persistencia de la Compra
        # Persistencia directa al ORM de Django (sin CompraRepository dedicado)
        compra = Compra.objects.create(
            usuario=usuario,
            fecha_visita=fecha_dt,
            monto_total=monto_total,
            forma_pago=forma_pago_codigo,
            estado_pago=estado_compra,
        )

        # 5. Creación de Entradas y Persistencia (Necesita el Pase para FK)
        tipos_requeridos = list(set([v["tipo_pase"] for v in visitantes]))
        # DELEGACIÓN: El Repositorio maneja la consulta eficiente y el mapeo
        pase_map = self.pase_repository.obtener_pases_como_diccionario(tipos_requeridos)

        entradas_a_crear = []
        for visitante in visitantes:
            precio_final = self._calcular_precio_entrada(visitante["edad"], visitante["tipo_pase"])
            pase_obj = pase_map.get(visitante["tipo_pase"])  # <-- Simple consulta al diccionario

            entradas_a_crear.append(Entrada(
                compra=compra,
                pase=pase_obj,
                edad_visitante=visitante["edad"],
                precio_calculado=precio_final
            ))

        Entrada.objects.bulk_create(entradas_a_crear)  # Uso eficiente del ORM

        # 6. Notificación
        confirmacion_email = self._enviar_confirmacion(usuario, compra)

        return compra, entradas_a_crear, confirmacion_email

    def _get_pago_strategy(self, tipo_pago: str) -> IEstrategiaPago:
        """Determina y retorna la estrategia de pago basada en el tipo."""
        if tipo_pago is None:
            raise ValueError("Forma de pago inválida: No especificada")

        tipo_pago_norm = tipo_pago.strip().capitalize()

        if tipo_pago_norm == "Tarjeta":
            return PagoTarjetaStrategy()
        elif tipo_pago_norm == "Efectivo":
            return PagoEfectivoStrategy()
        else:
            # Lanza excepción si el tipo es desconocido (e.g. "Cheque")
            raise ValueError(f"Forma de pago inválida: '{tipo_pago}' no reconocido")

    def _gestionar_pago(self, monto_total: float, tipo_pago: str) -> str:
        """
        Aplica el patrón Strategy para procesar el pago.
        Retorna el estado de la compra (ej. 'PAG', 'PEN').
        """
        # La validación de None/vacío se hace en comprar_entradas.
        estrategia = self._get_pago_strategy(tipo_pago)

        # pasarela_pagos es el recurso necesario por la estrategia de Tarjeta
        return estrategia.procesar_pago(monto_total, self.pasarela_pagos)

    def _calcular_precio_entrada(self, edad: int, tipo_pase: str) -> float:
        """Calculará el precio de una entrada según edad y tipo de pase."""

        costo = 0

        # Asigna según tipo de entrada
        if tipo_pase == 'Regular':
            costo = 5000
        elif tipo_pase == 'VIP':
            costo = 10000

        # Modifica segun edad
        if edad < 3:
            costo = 0
        elif edad < 10 or edad > 60:
            costo *= 0.5

        return costo

    def _calcular_monto_total(self, visitantes: list) -> float:
        """Calculará el monto total sumando todos los precios individuales."""

        suma = 0

        for visitante in visitantes:
            suma += self._calcular_precio_entrada(visitante["edad"], visitante["tipo_pase"])

        return suma

    # 3. Métodos de Validación (Deben fallar con NotImplementedError)

    def _validar_cantidad(self, cantidad, visitantes):
        """
        Valida que no se compren más de 10 entradas, que sea una cantidad positiva y que la cantidad coincida con los visitantes
        """

        # Validamos el rango valido
        if cantidad <= 0:
            raise ValueError("La cantidad de entradas debe ser al menos 1.")

        if cantidad > 10:
            raise LimiteEntradasExcedidoError("La cantidad de entradas no puede ser mayor a 10.")

        # Validamos que coincida con la cantidad de visitantes real
        if cantidad != len(visitantes):
            raise ValueError("La cantidad de entradas debe ser igual al nro de visitantes.")

    def _validar_fecha_hora_visita(self, fecha):
        """
        Valida que la fecha sea en un día donde el parque esté abierto.
        Considera la hora solo si la fecha es hoy, o si la fecha futura trae hora.
        Si la fecha futura no trae hora, se asume hora de apertura (09:00).
        """
        from datetime import datetime

        ahora = datetime.now()
        hoy = ahora.date()
        fecha_date = fecha.date()
        dia_fecha = fecha.weekday()

        # Feriados
        navidad = datetime(fecha.year, 12, 25).date()
        anio_nuevo = datetime(fecha.year, 1, 1).date()

        # 1️⃣ Fecha pasada
        if fecha_date < hoy:
            raise FechaInvalidaError("La fecha de visita ya pasó")

        # 2️⃣ Día cerrado: lunes o feriados
        if dia_fecha == 0 or fecha_date in [navidad, anio_nuevo]:
            raise ParqueCerradoError("El parque está cerrado en la fecha seleccionada")

        # 3️⃣ Validar hora
        hora = fecha.hour

        if fecha_date == hoy:
            # Si no se especificó hora (viene 00:00)
            if fecha.hour == 0 and fecha.minute == 0 and fecha.second == 0:
                # Si la hora actual es antes de las 19, permitir
                if ahora.hour >= 19:
                    raise ParqueCerradoError("El parque ya no abre hoy")
            else:
                # Si sí se especificó hora, validar rango
                if hora < 9 or hora >= 19:
                    raise ParqueCerradoError("El parque ya no abre hoy")
        else:
            # Fecha futura
            if fecha.hour != 0 or fecha.minute != 0 or fecha.second != 0:
                # Si el usuario especificó hora, validarla
                if hora < 9 or hora >= 19:
                    raise ParqueCerradoError("El parque no abre en ese horario para la fecha seleccionada")
            else:
                # Si no especificó hora, asumir apertura
                fecha = fecha.replace(hour=9, minute=0, second=0)

    def _validar_valores_pases(self, visitantes: list):
        """
        Valida que los 'tipo_pase' existan (ej. 'Regular', 'VIP').
        Será implementado en fase GREEN.
        """
        # 1. Obtener los tipos de pase válidos de la Capa de Datos (Repository)
        tipos_validos = self.pase_repository.obtener_tipos_de_pase_validos()

        if not tipos_validos:
            # Caso de borde si la DB está vacía
            raise ValueError("Error de configuración: No hay tipos de pases disponibles.")

        # 2. Iterar y validar contra la lista válida
        for i, visitante in enumerate(visitantes):
            tipo_pase = visitante.get("tipo_pase")

            # Asumimos que el formato (string no vacío) fue validado previamente

            if tipo_pase not in tipos_validos:
                # Usamos ValueError como el test requiere
                raise ValueError(f"Tipo de pase desconocido: '{tipo_pase}'.")

        return True

    def _validar_formato_fecha(self, fecha_str: str) -> datetime:
        """
        Valida que la fecha sea un string no vacío y que tenga formato ISO 8601 (YYYY-MM-DDThh:mm:ss).
        Retorna el objeto datetime si es válido.
        """
        # 1. Validación de ausencia (None o string vacío)
        if fecha_str is None or fecha_str == "":
            raise ValueError("La fecha de visita no fue proporcionada.")

        # 2. Validación de tipo (Debe ser un string)
        # Esto cubre el caso donde 12345 (int) se pasa como argumento.
        if not isinstance(fecha_str, str):
            raise ValueError("La fecha de visita debe ser un texto.")

        # 3. Validación de formato (ISO 8601)
        try:
            # El formato esperado es YYYY-MM-DDThh:mm:ss
            fecha_dt = datetime.fromisoformat(fecha_str)
            return fecha_dt
        except ValueError:
            # Atrapa cualquier error de parseo que no cumpla con el formato ISO
            raise ValueError("El formato de la fecha es inválido.")

    def _validar_formato_cantidad(self, cantidad):
        """Valida que la cantidad sea un entero."""

        # La validación explícita de tipo 'int' asegura que los float (5.0) y otros tipos fallen.
        if not isinstance(cantidad, int):
            raise ValueError("La cantidad de entradas debe ser un número entero.")

        # Si es un entero, simplemente retorna (o no hace nada, lo que permite que el 'try' del test pase)
        return True

    def _validar_formato_edades(self, visitantes: list):
        """Valida que la clave 'edad' exista, sea un entero y no sea negativa/muy alta."""
        max_edad_razonable = 120  # Límite superior para la edad

        for i, visitante in enumerate(visitantes):
            # 1. Validar existencia de la clave 'edad'
            if "edad" not in visitante:
                raise EdadInvalidaError(f"Falta 'edad' para un visitante (índice {i}).")

            edad = visitante["edad"]

            # 2. Validar tipo (debe ser un entero, excluye None, string, float, etc.)
            if not isinstance(edad, int):
                # Esto cubre fallos para string, float (30.5), y None
                raise EdadInvalidaError("La edad debe ser un número entero.")

            # 3. Validar edad negativa
            if edad < 0:
                raise EdadInvalidaError("La edad no puede ser negativa.")

            # 4. Validar edad irrealmente alta
            if edad > max_edad_razonable:
                raise EdadInvalidaError("La edad proporcionada parece irreal.")

        # Si el bucle termina sin errores, las edades son válidas.
        return True

    def _validar_formato_pases(self, visitantes: list):
        """Valida que la clave 'tipo_pase' exista, sea un string y no esté vacío/None/tipo incorrecto."""
        for i, visitante in enumerate(visitantes):
            # 1. Validar existencia de la clave 'tipo_pase'
            if "tipo_pase" not in visitante:
                raise ValueError(f"Falta la clave 'tipo_pase' para el visitante (índice {i}).")

            tipo_pase = visitante["tipo_pase"]

            # 2. Validar tipo (debe ser un string, cubriendo casos None y otros tipos incorrectos)
            if not isinstance(tipo_pase, str):
                # Esto cubre fallos para None, int, float, etc.
                raise ValueError("El 'tipo_pase' debe ser texto.")

            # 3. Validar string vacío
            if not tipo_pase.strip():
                # .strip() maneja tanto "" como " " (solo espacios en blanco)
                raise ValueError("El 'tipo_pase' no puede estar vacío.")

            # Si el bucle termina sin errores, los formatos son válidos.
        return True

    def _validar_forma_pago(self, tipo_pago: str) -> str:
        """
        Valida que el tipo de pago sea una cadena válida ('Tarjeta' o 'Efectivo')
        y devuelve el código correspondiente definido en Compra.FormasPago.
        """
        # 1. Manejar None y validar tipo ANTES de strip()
        if tipo_pago is None:
            # Corregido el mensaje para que coincida con la aserción del test.
            raise ValueError("Forma de pago inválida: No especificada")

        if not isinstance(tipo_pago, str):
            # Tu test no prueba esto directamente, pero está bien mantenerlo.
            raise ValueError("La forma de pago debe ser un texto.")

        # 2. Manejar string vacío después de strip()
        tipo_pago = tipo_pago.strip()
        if not tipo_pago:
            # Corregido el mensaje para que coincida con la aserción del test.
            raise ValueError("Forma de pago inválida: No especificada")
            # El test pide 'No especificada' para vacío/none.
            # Alternativa: raise ValueError("Forma de pago inválida: valor vacío o nulo.")

        tipo_pago_lower = tipo_pago.lower()

        if tipo_pago_lower == "tarjeta":
            return Compra.FormasPago.TARJETA  # "TAR"
        elif tipo_pago_lower == "efectivo":
            return Compra.FormasPago.EFECTIVO  # "EFE"
        else:
            # Corregido el mensaje para que coincida con la aserción del test.
            raise ValueError(f"Forma de pago inválida: '{tipo_pago}' no reconocido")


    def _validar_formato_usuario(self, usuario):
        """
        Valida que el objeto usuario tenga la estructura esperada.
        """

        # Caso 1: Usuario no proporcionado
        if usuario is None:
            raise ValueError("No se proporcionó información del usuario")

        # Lista de atributos obligatorios
        atributos_requeridos = ["first_name", "email", "esta_registrado"]

        # Caso 2: Falta algún atributo requerido
        for atributo in atributos_requeridos:
            if not hasattr(usuario, atributo):
                raise ValueError(f"Falta el atributo '{atributo}'")

        # Caso 3: Validar contenido de nombre
        if not isinstance(usuario.first_name, str) or usuario.first_name.strip() == "":
            raise ValueError("El atributo 'first_name' no puede estar vacío")

        # Caso 4: Validar contenido de email
        if not isinstance(usuario.email, str) or usuario.email.strip() == "":
            raise ValueError("El atributo 'email' no puede estar vacío")

        # Caso 5: Validar tipo de 'esta_registrado'
        if not isinstance(usuario.esta_registrado, bool):
            raise ValueError("El atributo 'esta_registrado' debe ser de tipo bool")

        # Si todo es correcto, no hace falta retornar nada (la validación pasa)
        return True

    def _validar_usuario(self, usuario: User):
        """
        Valida que el usuario esté registrado.
        """
        if not getattr(usuario, "esta_registrado", False):
            raise PermissionError("Usuario no registrado")

        return True

    def _enviar_confirmacion(self, usuario: User, compra):
        """
        Envía el correo de confirmación de la compra.
        Devuelve True si el envío fue exitoso, False en caso contrario.
        """

        try:
            # Llamar al servicio de correo con los parámetros esperados
            resultado = self.servicio_correo.enviar_confirmacion(
                mail=usuario.email,
                compra_details=compra.__dict__
            )

            # Si el servicio devolvió True, se considera exitoso
            if resultado:
                return True
            else:
                # Si el servicio devolvió False, se maneja como fallo
                return False

        except Exception:
            # Si ocurre cualquier excepción (error de red, etc.), manejarla
            return False

    def _enviar_notificacion(self, usuario: User, compra):
        """Envía notificaciones."""
        raise NotImplementedError("Método pendiente de implementación en fase GREEN.")
    