// hooks/useCompraEntradas.js
import { useState } from 'react';
import { servicioCompra } from '../services/entradasService';

export const useCompraEntradas = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const procesarCompra = async (datosCompra) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🚀 Iniciando procesamiento de compra...');
      const resultado = await servicioCompra.procesarCompra(datosCompra);
      console.log('💡 Resultado desde servicioCompra:', resultado);
      
      // Mensaje de confirmación para el email - MANTENIDO
      const mensajeMail = `
        ¡Gracias por tu compra en EcoHarmony Park!
        
        Detalles de tu reserva:
        - Fecha de visita: ${new Date(datosCompra.fecha_visita).toLocaleDateString('es-ES')}
        - Cantidad de entradas: ${datosCompra.cantidad_entradas}
        - Total: $${datosCompra.total.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        - Método de pago: ${datosCompra.forma_pago === 'tarjeta' ? 'Tarjeta' : 'Efectivo'}
        - Email: ${datosCompra.email}
        
        Detalles de las entradas:
        ${datosCompra.entradas.map((entrada, index) => `
          Visitante ${index + 1}:
          - Edad: ${entrada.edad} años
          - Tipo de pase: ${entrada.tipo_pase.toUpperCase()}
          - Precio: $${entrada.precio.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        `).join('')}
        
        Presenta este comprobante en la entrada del parque.
        ¡Te esperamos!
      `;

      console.log('✅ Compra procesada exitosamente');
      return { 
        compra: resultado, 
        mensajeMail,
        datosOriginales: datosCompra
      };
    } catch (err) {
      console.error('❌ Error en procesarCompra:', err);
      const errorMessage = err.message || 'Error al procesar la compra';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  return {
    procesarCompra,
    loading,
    error,
    clearError
  };
};