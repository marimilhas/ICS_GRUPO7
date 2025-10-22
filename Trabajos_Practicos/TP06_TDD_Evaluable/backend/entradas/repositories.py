from .models import Pase
from typing import Set


class PaseRepository:
    """Gateway de acceso a datos para el modelo Pase."""

    def obtener_tipos_de_pase_validos(self) -> Set[str]:
        """Consulta la DB y retorna un conjunto de strings de tipos de pase."""

        # Se podría cachear esta lista si no cambia a menudo.
        # Aquí consultamos directamente el ORM de Django.
        tipos_validos = Pase.objects.values_list('tipo', flat=True)
        return set(tipos_validos)