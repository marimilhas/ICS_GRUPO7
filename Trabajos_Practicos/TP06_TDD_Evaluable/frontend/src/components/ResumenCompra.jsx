import React from "react";

const ResumenCompra = ({ compra }) => {
  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-green-50 border border-green-200 rounded-2xl shadow-md">
      <h2 className="text-2xl font-bold text-green-800 mb-4 text-center">
        Resumen de Compra
      </h2>
      <ul className="text-gray-700 space-y-1">
        <li><strong>Fecha de Visita:</strong> {compra.fechaVisita}</li>
        <li><strong>Cantidad de Entradas:</strong> {compra.entradas.length}</li>
        <li><strong>Tipo de Pase:</strong> {compra.entradas[0].pase}</li>
        <li><strong>Edad:</strong> {compra.entradas[0].edad}</li>
        <li><strong>Forma de Pago:</strong> {compra.formaPago}</li>
      </ul>
    </div>
  );
};

export default ResumenCompra;
