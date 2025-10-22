import api from './api';

export const entradasService = {
  // Pases
  getPases: () => api.get('/pases/'),
  getPaseById: (id) => api.get(`/pases/${id}/`),

  // Compras
  getCompras: () => api.get('/compras/'),
  getCompraById: (id) => api.get(`/compras/${id}/`),
  createCompra: (compraData) => {
    // Formatear datos para el backend
    const compraFormateada = {
      fecha_visita: compraData.fecha_visita,
      forma_pago: compraData.forma_pago === 'tarjeta' ? 'TAR' : 'EFE',
      monto_total: compraData.total,
      estado_pago: compraData.forma_pago === 'tarjeta' ? 'PRO' : 'PEN', // PRO = procesando, PEN = pendiente
      email: compraData.email,
      cantidad_entradas: compraData.cantidad_entradas,
      usuario: compraData.usuario || 2  // Usuario demo por defecto
    };
    return api.post('/compras/', compraFormateada);
  },
  updateCompra: (id, compraData) => api.put(`/compras/${id}/`, compraData),
  deleteCompra: (id) => api.delete(`/compras/${id}/`),

  // Entradas
  getEntradas: () => api.get('/entradas/'),
  getEntradaById: (id) => api.get(`/entradas/${id}/`),
  createEntrada: (entradaData) => api.post('/entradas/', entradaData),
  
  // Procesar pago (para tarjetas)
  procesarPago: (compraId, datosPago) => api.post(`/compras/${compraId}/procesar-pago/`, datosPago),
};

// Servicio para procesar compras con la lógica de negocio - ACTUALIZADO
export const servicioCompra = {
  procesarCompra: async (datosCompra) => {
    try {
      console.log('Datos recibidos para procesar compra:', datosCompra);

      // Primero crear la compra con usuario
      const compraResponse = await entradasService.createCompra({
        fecha_visita: datosCompra.fecha_visita,
        forma_pago: datosCompra.forma_pago,
        monto_total: datosCompra.total,
        estado_pago: datosCompra.forma_pago === 'tarjeta' ? 'PRO' : 'PEN',
        email: datosCompra.email,
        cantidad_entradas: datosCompra.cantidad_entradas,
        usuario: 2 // Usuario demo
      });

      const compra = compraResponse.data;
      console.log('Compra creada:', compra);

      // Luego crear las entradas asociadas
      const entradasPromises = datosCompra.entradas.map((entrada) => {
        // Determinar el pase_id basado en el tipo de entrada
        const paseId = entrada.tipo_pase === 'VIP' ? 2 : 1; // Ajusta según tus IDs
        
        return entradasService.createEntrada({
          compra: compra.id,
          pase: paseId,
          edad_visitante: entrada.edad,
          precio_calculado: entrada.precio
        });
      });

      const entradasCreadas = await Promise.all(entradasPromises);
      console.log('Entradas creadas:', entradasCreadas);

      // Si es pago con tarjeta, procesar el pago
      if (datosCompra.forma_pago === 'tarjeta') {
        try {
          const pagoResponse = await entradasService.procesarPago(compra.id, {
            // Aquí irían los datos de la tarjeta si los necesitas
            metodo: 'mercadopago' // o la pasarela que uses
          });
          console.log('Pago procesado:', pagoResponse.data);
        } catch (pagoError) {
          console.error('Error procesando pago:', pagoError);
          // No lanzamos error aquí para no revertir la compra creada
        }
      }

      // Retornar compra con entradas para el frontend
      return {
        ...compra,
        entradas: entradasCreadas.map(entrada => entrada.data)
      };

    } catch (error) {
      console.error('Error en procesarCompra:', error);
      
      // Mejor manejo de errores
      if (error.response) {
        // Error del servidor
        throw new Error(error.response.data.detail || error.response.data.message || 'Error del servidor');
      } else if (error.request) {
        // Error de red
        throw new Error('Error de conexión con el servidor');
      } else {
        // Error inesperado
        throw new Error('Error inesperado al procesar la compra');
      }
    }
  }
};