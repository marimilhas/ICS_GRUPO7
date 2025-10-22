import { useState } from 'react';
import { servicioCompra } from '../services/entradasService';

export const useCompraEntradas = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const procesarCompra = async (datosCompra) => {
    setLoading(true);
    setError(null);
    
    try {
      const compraProcesada = await servicioCompra.procesarCompra(datosCompra);
      
      // Mensaje de confirmación para el email - ACTUALIZADO
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

      return { 
        compra: compraProcesada, 
        mensajeMail,
        datosOriginales: datosCompra // Para mantener compatibilidad
      };
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.response?.data || 'Error al procesar la compra';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    procesarCompra,
    loading,
    error
  };
};