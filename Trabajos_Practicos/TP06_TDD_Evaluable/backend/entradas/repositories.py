from typing import Set, Dict
from .models import Pase


class PaseRepository:
    """Gateway de acceso a datos para el modelo Pase."""

    def obtener_tipos_de_pase_validos(self) -> Set[str]:
        """Consulta la DB y retorna un conjunto de strings de tipos de pase."""

        # Se podría cachear esta lista si no cambia a menudo.
        # Aquí consultamos directamente el ORM de Django.
        tipos_validos = Pase.objects.values_list('tipo', flat=True)
        return set(tipos_validos)

    def obtener_pases_como_diccionario(self, tipos_pases: list) -> Dict[str, Pase]:
        """
        Retorna un diccionario mapeando el nombre del pase (str) a la instancia de Pase.
        Simplifica la búsqueda y evita la lógica compleja de cacheo en el servicio.
        """
        pases = Pase.objects.filter(tipo__in=tipos_pases)
        # Mapea { 'VIP': <Pase obj VIP>, 'Regular': <Pase obj Regular> }
        return {p.tipo: p for p in pases}