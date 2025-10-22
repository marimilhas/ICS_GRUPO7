import React from "react";

const Confirmacion = ({ mensaje, compra }) => {

  // Contar cantidad de pases por tipo
  const cantidadRegulares = compra.entradas.filter(e => e.pase === "regular").length;
  const cantidadVIP = compra.entradas.filter(e => e.pase === "VIP").length;

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-100 text-center">
      <div className="w-16 h-16 bg-green-light/30 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-green-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>

      <h2 className="text-2xl font-bold text-green-dark mb-4">
        ¡Compra Confirmada!
      </h2>

      <div className="bg-green-light/20 border border-green-light rounded-lg p-6 mb-6">
        <p className="text-green-dark mb-4">{mensaje}</p>

        {compra && (
          <div className="text-sm text-green-dark space-y-2 text-left">
            <p><strong>Fecha de visita:</strong> {new Date(compra.fecha).toLocaleDateString('es-ES')}</p>
            <p><strong>Cantidad de entradas:</strong> {compra.cantidad} ({cantidadRegulares} regulares y {cantidadVIP} VIP)</p>
            <p><strong>Método de pago:</strong> {compra.formaPago === 'tarjeta' ? 'Tarjeta (Mercado Pago)' : 'Efectivo'}</p>
          </div>
        )}
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          <strong>¡Importante!</strong> Se ha enviado un email de confirmación con los detalles de tu compra.
          {compra?.formaPago === 'tarjeta' && ' El pago se procesó exitosamente a través de Mercado Pago.'}
          {compra?.formaPago === 'efectivo' && ' Recuerda llevar el comprobante para pagar en boletería.'}
        </p>
      </div>
    </div>
  );
};

export default Confirmacion;