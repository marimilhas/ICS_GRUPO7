import React from "react";

const ResumenCompra = ({ compra }) => {
  const calcularTotal = () => {
    const precio = compra.entradas[0]?.pase === "regular" ? 1.0 : 0.7;
    return (precio * compra.entradas.length).toFixed(2);
  };
// en edad del visitante me muestra solo la edad del primer visitante, no de todos
// para mi ahi deberia ir la edad de el que hizo la compra, y eso se arregla con el login
// se autocompltaria con la edad del usuario logueado --> VER
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-100">
      <h2 className="text-2xl font-bold text-green-800 mb-6 text-center">
        Resumen de tu Compra
      </h2>

      <div className="space-y-6">
        {/* Información General */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-2">Fecha de Visita</h3>
            <p className="text-lg">{new Date(compra.fechaVisita).toLocaleDateString('es-ES')}</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-2">Cantidad de Entradas</h3>
            <p className="text-lg">{compra.cantidadEntradas}</p>
          </div>
        </div>

        {/* Detalles de la Compra */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-700 mb-3">Detalles</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Tipo de Pase:</span>
              <span className={`font-medium ${compra.entradas[0]?.pase === 'VIP' ? 'text-purple-600' : 'text-blue-600'}`}>
                {compra.entradas[0]?.pase?.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Edad del Visitante:</span> 
              <span className="font-medium">{compra.entradas[0]?.edad} años</span>
            </div>
            <div className="flex justify-between">
              <span>Método de Pago:</span>
              <span className="font-medium capitalize">
                {compra.forma_pago === 'tarjeta' ? 'Tarjeta (Mercado Pago)' : 'Efectivo'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Email:</span>
              <span className="font-medium">{compra.usuario?.mail}</span>
            </div>
          </div>
        </div>

        {/* Total */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Total a Pagar:</span>
            <span className="text-green-800">${calcularTotal()}</span>
          </div>
        </div>

        {/* Información adicional */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">Información Importante</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Presentar este resumen en la entrada del parque</li>
            <li>• Llegar 15 minutos antes de la hora programada</li>
            {compra.forma_pago === 'efectivo' && (
              <li>• Pago en efectivo se realiza al ingresar al parque</li>
            )}
            {compra.forma_pago === 'tarjeta' && (
              <li>• Serás redirigido a Mercado Pago para el pago</li>
              // obvio esto FALTA, no se esta redirigiendo a ningun lado
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ResumenCompra;