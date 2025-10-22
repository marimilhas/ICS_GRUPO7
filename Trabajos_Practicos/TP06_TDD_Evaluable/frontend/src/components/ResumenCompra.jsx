import React from "react";

const ResumenCompra = ({ compra }) => {

  // Agrupamos y contamos las edades (para mostrarlas más lindo en el resumen)
  const edadesAgrupadas = compra.entradas
    .map(e => e.edad) // extraemos las edades
    .sort((a, b) => a - b)
    .reduce((acc, edad) => {
      acc[edad] = (acc[edad] || 0) + 1;
      return acc;
    }, {});

  // Convertimos a array para renderizar
  const edadesRender = Object.entries(edadesAgrupadas);

  // Contar cantidad de pases por tipo
  const cantidadRegulares = compra.entradas.filter(e => e.pase === "regular").length;
  const cantidadVIP = compra.entradas.filter(e => e.pase === "VIP").length;


  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-light">
      <h2 className="text-2xl font-bold text-green-dark mb-6 text-center">
        Resumen de tu Compra
      </h2>

      <div className="space-y-6">
        {/* Información General */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-pale/25 p-4 rounded-lg">
            <h3 className="font-semibold text-green-dark mb-2">Fecha de Visita</h3>
            <p className="text-lg">{new Date(compra.fecha).toLocaleDateString('es-ES')}</p>
          </div>

          <div className="bg-green-pale/25 p-4 rounded-lg">
            <h3 className="font-semibold text-green-dark mb-2">Cantidad de Entradas</h3>
            <p className="text-lg">{compra.cantidad}</p>
          </div>
        </div>

        {/* Detalles de la Compra */}
        <div className="bg-green-pale/25 p-4 rounded-lg">
          <h3 className="font-semibold text-green-dark mb-3">Detalles</h3>
          <div className="space-y-2">

            <div className="flex justify-between">
              <span className="font-medium text-left">Pases regulares:</span>
              <span className="font-medium capitalize">
                {cantidadRegulares}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="font-medium text-left">Pases VIP:</span>
              <span className="font-medium capitalize">
                {cantidadVIP}
              </span>
            </div>

            <div className="flex justify-between items-start gap-4">
              <span className="font-medium text-left">
                Edades de los Visitantes:
              </span>

              <div className="flex flex-col sm:flex-row flex-wrap justify-end gap-2 max-w-[60%] md:max-w-[65%] lg:max-w-[60%]">
                {edadesRender.map(([edad, cantidad], index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-green-pale/70 rounded text-center whitespace-nowrap"
                  >
                    {cantidad > 1
                      ? `${cantidad} x ${edad} ${edad === '1' ? 'año' : 'años'}`
                      : `${edad} ${edad === '1' ? 'año' : 'años'}`}
                  </span>
                ))}
              </div>
            </div>


            <div className="flex justify-between">
              <span className="font-medium text-left">Método de Pago:</span>
              <span className="font-medium capitalize">
                {compra.formaPago === 'tarjeta' ? 'Tarjeta (Mercado Pago)' : 'Efectivo'}
              </span>
            </div>

            <div className="flex justify-between">
              <span>Email:</span>
              <span className="font-medium">{compra.mail}</span>
            </div>
          </div>
        </div>

        {/* Total */}
        <div className="bg-green-light/20 border border-green-light rounded-lg p-4">
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Total a Pagar:</span>
            <span className="text-green-dark">${compra.total}</span>
          </div>
        </div>

        {/* Información adicional */}
        <div className="bg-green-light/20 border border-green-light rounded-lg p-4">
          <h4 className="font-bold text-green-dark mb-2">Información Importante</h4>
          <ul className="text-sm text-green-dark space-y-1">
            <li>• Presentar este resumen en la entrada del parque</li>
            <li>• Llegar 15 minutos antes de la hora programada</li>
            {compra.formaPago === 'efectivo' && (
              <li>• Pago en efectivo se realiza al ingresar al parque</li>
            )}
            {compra.formaPago === 'tarjeta' && (
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