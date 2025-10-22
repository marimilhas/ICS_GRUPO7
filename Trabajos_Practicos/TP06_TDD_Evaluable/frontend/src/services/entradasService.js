// services/entradasService.js
import api from './api';

export const entradasService = {
  // Pases
  getPases: () => api.get('/pases/'),
  getPaseById: (id) => api.get(`/pases/${id}/`),

  // Compras
  getCompras: () => api.get('/compras/'),
  getCompraById: (id) => api.get(`/compras/${id}/`),
  createCompra: (compraData) => {
    console.log('📤 Datos enviados al backend:', compraData);
    return api.post('/compras/', compraData);
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

// Servicio para procesar compras - COMPLETAMENTE CORREGIDO
export const servicioCompra = {
  procesarCompra: async (datosCompra) => {
    try {
      console.log('📦 Datos recibidos para procesar compra:', datosCompra);

      // CORRECCIÓN: Usar los valores EXACTOS que el backend Django espera ('TAR' y 'EFE')
      const formaPagoBackend = datosCompra.forma_pago === 'tarjeta' ? 'TAR' : 'EFE';

      // TRANSFORMAR DATOS al formato que espera el backend
      const datosParaBackend = {
        cantidad: datosCompra.cantidad_entradas,
        fecha_visita: datosCompra.fecha_visita,
        forma_pago: formaPagoBackend, // 'TAR' o 'EFE' - valores exactos del backend
        visitantes: datosCompra.entradas.map(entrada => ({
          edad: entrada.edad,
          tipo_pase: entrada.tipo_pase.charAt(0).toUpperCase() + entrada.tipo_pase.slice(1) // Capitalizar
        })),
        usuario: {
          nombre: datosCompra.nombre || "Cliente",
          email: datosCompra.email,
          esta_registrado: true
        },
        monto_total: datosCompra.total // Agregar monto_total que el backend requiere
      };

      console.log('🔄 Datos transformados para backend:', datosParaBackend);

      // Crear la compra en el backend
      const compraResponse = await entradasService.createCompra(datosParaBackend);
      const compra = compraResponse.data;
      console.log('✅ Compra creada en backend:', compra);

      // Si necesitas crear entradas individualmente (depende de tu backend)
      try {
        const entradasPromises = datosCompra.entradas.map((entrada, index) => {
          return entradasService.createEntrada({
            compra: compra.id,
            visitante_index: index,
            edad: entrada.edad,
            tipo_pase: entrada.tipo_pase,
            precio: entrada.precio
          });
        });

        const entradasCreadas = await Promise.all(entradasPromises);
        console.log('🎫 Entradas creadas:', entradasCreadas);
        
        // Retornar compra con entradas
        return {
          ...compra,
          entradas: entradasCreadas.map(entrada => entrada.data)
        };
      } catch (entradasError) {
        console.warn('⚠️ Error creando entradas individuales, pero compra fue creada:', entradasError);
        return compra; // Retornar compra aunque falle la creación de entradas individuales
      }

    } catch (error) {
      console.error('❌ Error en procesarCompra:', error);
      
      // Mejor manejo de errores
      if (error.response) {
        const errorData = error.response.data;
        console.error('📋 Detalles del error del servidor:', errorData);
        
        // Mensajes más específicos según el error
        if (errorData.forma_pago) {
          throw new Error(`Error en forma de pago: ${errorData.forma_pago.join(', ')}`);
        }
        if (errorData.monto_total) {
          throw new Error(`Error en monto total: ${errorData.monto_total.join(', ')}`);
        }
        if (errorData.visitantes) {
          throw new Error(`Error en datos de visitantes: ${errorData.visitantes.join(', ')}`);
        }
        
        throw new Error(errorData.detail || errorData.message || JSON.stringify(errorData));
      } else if (error.request) {
        throw new Error('❌ Error de conexión con el servidor. Verifica que el backend esté ejecutándose.');
      } else {
        throw new Error('❌ Error inesperado al procesar la compra');
      }
    }
  }
};