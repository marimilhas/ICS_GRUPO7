from rest_framework import serializers
from django.contrib.auth.models import User 
from entradas.models import Pase, Compra, Entrada

# --- Serializadores Base ---

class PaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pase
        fields = '__all__'

# --- Serializador Corregido para Entrada ---

class EntradaSerializer(serializers.ModelSerializer):
    # Campos de entrada (solo escritura)
    edad = serializers.IntegerField(write_only=True) 
    precio = serializers.DecimalField(max_digits=8, decimal_places=2, write_only=True) # <-- AHORA ES write_only
    tipo_pase = serializers.CharField(write_only=True) 
    
    # Detalle del Pase para la respuesta de lectura
    pase_detalle = PaseSerializer(source='pase', read_only=True)

    class Meta:
        model = Entrada
        # CORRECCIÓN CLAVE: NO incluir 'edad_visitante' ni 'precio_calculado' en la lista fields
        # ya que serán añadidos manualmente en create().
        fields = ['id', 'compra', 'pase', 'tipo_pase', 'pase_detalle', 'edad', 'precio']
        
        # 'pase' es read_only. 'precio_calculado' NO debe ser read_only_fields 
        # si queremos que aparezca en la respuesta de lectura, pero lo manejamos manualmente.
        read_only_fields = ['pase'] # Solo el pase es read_only si se quiere ver en la respuesta
    
    def create(self, validated_data):
        # 1. Extracción y Mapeo: EDAD (Soluciona NOT NULL en edad_visitante)
        edad_valor = validated_data.pop('edad')
        validated_data['edad_visitante'] = edad_valor # Mapeo manual
        
        # 2. Extracción y Mapeo: PRECIO (Soluciona NOT NULL en precio_calculado)
        precio_valor = validated_data.pop('precio')
        validated_data['precio_calculado'] = precio_valor # Mapeo manual

        # 3. Extracción y Lógica "GET OR CREATE"
        tipo_pase_nombre = validated_data.pop('tipo_pase')
        
        # 4. Lógica "GET OR CREATE" del Pase
        # Usamos el precio recién mapeado como fallback
        precio_fallback = precio_valor # Usamos el precio del request
        
        pase_obj, created = Pase.objects.get_or_create(
            tipo=tipo_pase_nombre,
            defaults={'precio': precio_fallback}
        )
        
        if created:
            print(f"INFO: El Pase tipo '{tipo_pase_nombre}' no existía y fue creado con precio ${precio_fallback}.")
            
        validated_data['pase'] = pase_obj

        # 5. Crear la Entrada (ahora con todos los campos obligatorios del modelo)
        return super().create(validated_data)


# --- Serializador Corregido para Compra (Sin cambios en esta iteración) ---

class CompraSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    entradas = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Compra
        fields = '__all__'
    
    def get_entradas(self, obj):
        from .serializers import EntradaSerializer 
        # CORRECCIÓN: Usar obj.entradas.all() (el related_name)
        return EntradaSerializer(obj.entradas.all(), many=True).data