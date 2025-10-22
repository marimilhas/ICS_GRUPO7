import React from "react";

const Confirmacion = ({ mensaje }) => {
  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-green-100 rounded-2xl shadow-md border border-green-200 text-center">
      <h2 className="text-3xl font-bold text-green-800 mb-3"> Compra Confirmada</h2>
      <p className="text-lg text-gray-700">{mensaje}</p>
      <p className="mt-2 font-medium text-green-700">¡Gracias por tu compra!</p>
    </div>
  );
};

export default Confirmacion;
