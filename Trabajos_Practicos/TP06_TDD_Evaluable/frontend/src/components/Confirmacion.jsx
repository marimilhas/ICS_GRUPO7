import React from "react";

const Confirmacion = ({ mensaje, compra }) => {
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-100 text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>
      
      <h2 className="text-2xl font-bold text-green-800 mb-4">
        ¡Compra Confirmada!
      </h2>
      
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
        <p className="text-gray-700 mb-4">{mensaje}</p>
        
        {compra && (
          <div className="text-sm text-gray-600 space-y-2 text-left">
            <p><strong>Fecha de visita:</strong> {new Date(compra.fechaVisita).toLocaleDateString('es-ES')}</p>
            <p><strong>Cantidad de entradas:</strong> {compra.cantidadEntradas}</p>
            <p><strong>Tipo de pase:</strong> {compra.entradas[0]?.pase?.toUpperCase()}</p>
            <p><strong>Método de pago:</strong> {compra.forma_pago === 'tarjeta' ? 'Tarjeta (Mercado Pago)' : 'Efectivo'}</p>
          </div>
        )}
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          <strong>¡Importante!</strong> Se ha enviado un email de confirmación con los detalles de tu compra. 
          {compra?.forma_pago === 'tarjeta' && ' El pago se procesó exitosamente a través de Mercado Pago.'}
          {compra?.forma_pago === 'efectivo' && ' Recuerda llevar el comprobante para pagar en boletería.'}
        </p>
      </div>
    </div>
  );
};

export default Confirmacion;