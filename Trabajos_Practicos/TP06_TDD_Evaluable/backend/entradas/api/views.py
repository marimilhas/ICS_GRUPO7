from rest_framework import viewsets
from entradas.models import Pase, Compra, Entrada
from .serializers import PaseSerializer, CompraSerializer, EntradaSerializer
from django.contrib.auth.models import User

class PaseViewSet(viewsets.ModelViewSet):
    queryset = Pase.objects.all()
    serializer_class = PaseSerializer

class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def perform_create(self, serializer):
        # Si no se proporciona usuario en los datos, usar usuario por defecto
        if 'usuario' not in serializer.validated_data:
            # Usuario por defecto (ID 2 para desarrollo)
            default_user = User.objects.get(id=2)
            serializer.save(usuario=default_user)
        else:
            serializer.save()

class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            # Log para debug
            print("Datos recibidos:", request.data)
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print("Error al crear entrada:", str(e))
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )