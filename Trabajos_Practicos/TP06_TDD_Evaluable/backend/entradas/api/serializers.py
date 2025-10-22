# entradas/api/serializers.py
from rest_framework import serializers
from entradas.models import Pase, Compra, Entrada
from django.contrib.auth.models import User

class PaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pase
        fields = '__all__'

class EntradaSerializer(serializers.ModelSerializer):
    # Cambiar a PrimaryKeyRelatedField para que sea escribible
    pase = serializers.PrimaryKeyRelatedField(
        queryset=Pase.objects.all()
    )
    
    # Opcional: mantener el serializer anidado para lectura
    pase_detalle = PaseSerializer(source='pase', read_only=True)

    class Meta:
        model = Entrada
        fields = '__all__'
        # O si quieres incluir el pase_detalle:
        # fields = ['id', 'compra', 'pase', 'pase_detalle', 'edad_visitante', 'precio_calculado']

class CompraSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    entradas = EntradaSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = '__all__'