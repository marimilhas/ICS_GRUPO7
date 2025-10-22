# servicio_compra.py

from django.contrib.auth.models import User
from .excepciones import LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError, FechaInvalidaError
from datetime import datetime, timedelta

from .repositories import PaseRepository


# Asegúrate de que las excepciones necesarias están definidas en excepciones.py
# from .excepciones import LimiteEntradasExcedidoError, ParqueCerradoError, PagoRechazadoError, EdadInvalidaError

class ServicioCompraEntradas:
    """Clase de la Capa de Lógica de Negocio (Service)."""

    def __init__(self, pasarela_pagos, servicio_correo, servicio_calendario, pase_repository: PaseRepository):
        self.pasarela_pagos = pasarela_pagos
        self.servicio_correo = servicio_correo
        self.servicio_calendario = servicio_calendario
        self.pase_repository = pase_repository  # <-- Nueva dependencia inyectada

    # 1. Método Principal (Debe fallar para los tests de integración)
    def comprar_entradas(self, usuario: User, cantidad: int, fecha_visita: str, tipo_pago: str, visitantes: list):
        """
        Método principal que orquesta la compra.
        Debe fallar en la Fase RED.
        """
        # La forma más limpia para un método no implementado en el flujo principal:
        raise NotImplementedError("Método comprar_entradas aún no implementado (Fase RED).")

    # 2. Métodos de Cálculo (Deben fallar para los tests de precio/monto)
    def _calcular_precio_entrada(self, edad: int, tipo_pase: str) -> float:
        """Calculará el precio de una entrada según edad y tipo de pase."""
        raise NotImplementedError("Método pendiente de implementación en fase GREEN.")

    def _calcular_monto_total(self, visitantes: list) -> float:
        """Calculará el monto total sumando todos los precios individuales."""
        # Nota: Este método ya tiene un NotImplementedError en el código que devolviste.
        # Si se deja así, todos los tests de cálculo fallarán con este error.
        raise NotImplementedError("Método pendiente de implementación en fase GREEN.")

    # 3. Métodos de Validación (Deben fallar con NotImplementedError)

    def _validar_cantidad(self, cantidad, visitantes):
        """
        Valida que no se compren más de 10 entradas, que sea una cantidad positiva y que la cantidad coincida con los visitantes
        """

        #Validamos el rango valido
        if cantidad <= 0:
            raise ValueError("La cantidad de entradas debe ser al menos 1.")
        
        if cantidad > 10:
            raise LimiteEntradasExcedidoError("La cantidad de entradas no puede ser mayor a 10.")
        
        #Validamos que coincida con la cantidad de visitantes real         
        if cantidad != len(visitantes):
            raise ValueError("La cantidad de entradas debe ser igual al nro de visitantes.")
        
        
        
    def _validar_fecha_hora_visita(self, fecha):
        """
        Valida que la fecha sea en un dia donde el parque esté abierto (ni lunes, ni feriados como navidad o año nuevo),
        que se compre durante horario habilitado
        """

        #Creamos las fechas y horas necesarias para comparacion
        dia_fecha = fecha.weekday()
        navidad = datetime(fecha.year, month=12, day=25) + timedelta(hours=fecha.hour, minutes=fecha.minute, seconds=fecha.second)
        anio_nuevo = datetime(fecha.year, month=1, day=1) + timedelta(hours=fecha.hour, minutes=fecha.minute, seconds=fecha.second)
        hora_fecha = fecha.hour

        if fecha == navidad or fecha == anio_nuevo or dia_fecha == 0 or hora_fecha < 9 or hora_fecha >= 19:
            raise ParqueCerradoError

        if fecha < datetime.now():
            raise FechaInvalidaError

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

    def _validar_formato_usuario(self, usuario):
        """
        Valida que el objeto usuario tenga la estructura esperada.
        """

        # Caso 1: Usuario no proporcionado
        if usuario is None:
            raise ValueError("No se proporcionó información del usuario")

        # Lista de atributos obligatorios
        atributos_requeridos = ["nombre", "email", "esta_registrado"]

        # Caso 2: Falta algún atributo requerido
        for atributo in atributos_requeridos:
            if not hasattr(usuario, atributo):
                raise ValueError(f"Falta el atributo '{atributo}'")

        # Caso 3: Validar contenido de nombre
        if not isinstance(usuario.nombre, str) or usuario.nombre.strip() == "":
            raise ValueError("El atributo 'nombre' no puede estar vacío")

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

    def _gestionar_pago(self, monto_total: float, tipo_pago: str) -> bool:
        """
        Procesa el pago (llama a pasarela si es Tarjeta) o lo registra (si es Efectivo).
        """

         # Validar que se haya especificado una forma de pago
        if tipo_pago is None:
            raise ValueError("Forma de pago inválida: No especificada")

        # Normalizamos el texto para evitar errores por mayúsculas/minúsculas
        tipo_pago = tipo_pago.strip().capitalize()

        # Manejar los distintos tipos de pago
        if tipo_pago == "Efectivo":
            # No se llama a la pasarela de pagos
            return True

        elif tipo_pago == "Tarjeta":
            # Llama a la pasarela de pagos
            resultado = self.pasarela_pagos.procesar_pago(monto=monto_total)

            if resultado:
                return True
            else:
                # Si la pasarela devuelve False, lanzar la excepción correspondiente
                raise PagoRechazadoError("El pago fue rechazado")

        else:
            # Cualquier otro tipo de pago no reconocido
            raise ValueError(f"Forma de pago inválida: '{tipo_pago}' no reconocido")


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