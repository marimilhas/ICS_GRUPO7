// services/entradasService.js

// Asumimos que 'api' es un cliente configurado (ej: axios)
import api from './api';

export const entradasService = {
  // Pases
  getPases: () => api.get('/pases/'),
  getPaseById: (id) => api.get(`/pases/${id}/`),

  // Compras
  getCompras: () => api.get('/compras/'),
  getCompraById: (id) => api.get(`/compras/${id}/`),
  createCompra: (compraData) => {
    console.log('📤 Datos finales enviados al backend:', compraData);
    // El endpoint de compra real es /compras/
    return api.post('/compras/', compraData);
  },
  updateCompra: (id, compraData) => api.put(`/compras/${id}/`, compraData),
  deleteCompra: (id) => api.delete(`/compras/${id}/`),

  // 💡 NUEVO MÉTODO: Endpoint para validación
  validateCompra: (compraData) => {
    console.log('📤 Datos enviados para validación:', compraData);
    // Asumimos que el endpoint para validación es /validar-compra/
    return api.post('/validar-compra/', compraData);
  }
};

// Servicio para procesar compras (usado por el hook useCompraEntradas)
export const servicioCompra = {
  procesarCompra: async (datosCompra) => {
    try {
      console.log('📦 Datos recibidos para procesar compra (Lógica final de compra/pago):', datosCompra);

      // El tipo de pase debe ser capitalizado para el backend
      const datosParaBackend = {
        cantidad: datosCompra.cantidad_entradas,
        fecha_visita: datosCompra.fecha_visita,
        forma_pago: datosCompra.forma_pago, // 'Tarjeta' o 'Efectivo'
        visitantes: datosCompra.entradas.map(entrada => ({
          edad: entrada.edad,
          tipo_pase: entrada.tipo_pase.charAt(0).toUpperCase() + entrada.tipo_pase.slice(1) // Capitalizar
        })),
        usuario: {
          nombre: datosCompra.nombre || "Cliente",
          email: datosCompra.email,
          esta_registrado: true
        },
        monto_total: datosCompra.total // Este ya viene del cálculo frontend/validación
      };

      console.log('🔄 Datos transformados para backend:', datosParaBackend);

      // Llama a la creación de la compra (que incluye pago y persistencia)
      const compraResponse = await entradasService.createCompra(datosParaBackend);
      console.log('✅ Compra response:', compraResponse.data);
      const compra = compraResponse.data.compra; // Asumiendo que la respuesta es {compra: {...}}
      const mensajeMail = compraResponse.data.mensajeMail;
      
      console.log('✅ Compra creada en backend:', compra);
      
      return { 
        compra: compra, 
        mensajeMail: mensajeMail
      };

    } catch (error) {
      console.error('❌ Error en procesarCompra (crear):', error);
      
      if (error.response) {
        const errorData = error.response.data;
        console.error('📋 Detalles del error del servidor:', errorData);
        throw new Error(errorData.error || errorData.detail || JSON.stringify(errorData));
      } else if (error.request) {
        throw new Error('❌ Error de conexión con el servidor. Verifica que el backend esté ejecutándose.');
      } else {
        throw new Error('❌ Error inesperado al procesar la compra');
      }
    }
  }
};
