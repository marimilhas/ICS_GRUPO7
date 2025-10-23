from rest_framework import viewsets, mixins
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User 
from entradas.models import Pase, Compra, Entrada
from .serializers import PaseSerializer, CompraSerializer, EntradaSerializer

# --- Vistas (ViewSets) ---

class PaseViewSet(viewsets.ModelViewSet):
    queryset = Pase.objects.all()
    serializer_class = PaseSerializer

class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def perform_create(self, serializer):
        # Usamos el usuario autenticado si existe
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            # 1. Obtener o crear un usuario de simulación (si no hay autenticación)
            # Esto garantiza que el ID exista
            usuario, creado = User.objects.get_or_create(
                username='simulador_compra',
                defaults={'email': 'simulador@parque.com', 'password': 'simulador_pw'}
            )

        # 2. Asignar el usuario y guardar
        serializer.save(usuario=usuario)

class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            print("Datos recibidos:", request.data)
            # El super().create se encarga de llamar a serializer.is_valid()
            # y luego a serializer.create() (donde está tu lógica 'get_or_create')
            return super().create(request, *args, **kwargs)
        
        except Exception as e:
            # Captura y manejo limpio de errores
            if isinstance(e, ValidationError):
                 error_detail = e.detail
                 print("Error de validación al crear entrada:", error_detail)
            else:
                 error_detail = {"detail": str(e)}
                 print("Error interno al crear entrada:", str(e))
                 
            return Response(
                {"error": "Error al procesar la entrada", "details": error_detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )