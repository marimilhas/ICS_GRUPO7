import React, { useState } from "react";

const FormularioCompra = ({ onCompra }) => {
  const [fecha, setFecha] = useState("");
  const [cantidad, setCantidad] = useState(1);
  const [edad, setEdad] = useState(18);
  const [pase, setPase] = useState("regular");
  const [formaPago, setFormaPago] = useState("tarjeta");
  const [mail, setMail] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const usuario = { mail };
    const entradas = Array(cantidad).fill({ fecha, pase, edad });
    const compraData = { entradas, forma_pago: formaPago, usuario };

    try {
      const res = await fetch("http://localhost:8000/compras", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(compraData),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }

      const data = await res.json();
      onCompra(data.compra, data.mensaje);
    } catch {
      alert("Error al conectarse con el servidor");
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-100">
      <h2 className="text-3xl font-bold text-green-700 mb-8 text-center">
         Comprar Entradas
      </h2>

      {/* Selector de Tipo de Pase - Estilo Tarjeta */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Selecciona tu Pase</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pase Regular */}
          <div 
            className={`border-2 rounded-xl p-6 cursor-pointer transition-all duration-300 ${
              pase === "regular" 
                ? "border-green-500 bg-green-50 shadow-md" 
                : "border-gray-200 hover:border-green-300"
            }`}
            onClick={() => setPase("regular")}
          >
            <div className="flex justify-between items-start mb-4">
              <h4 className="text-lg font-bold text-gray-800">Pase Regular</h4>
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                100% ATA
              </div>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>...</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>...</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <span className="text-2xl font-bold text-gray-900">$1.0</span>
              <span className="text-sm text-gray-500 ml-2">por persona</span>
            </div>
          </div>

          {/* Pase VIP */}
          <div 
            className={`border-2 rounded-xl p-6 cursor-pointer transition-all duration-300 ${
              pase === "VIP" 
                ? "border-purple-500 bg-purple-50 shadow-md" 
                : "border-gray-200 hover:border-purple-300"
            }`}
            onClick={() => setPase("VIP")}
          >
            <div className="flex justify-between items-start mb-4">
              <h4 className="text-lg font-bold text-gray-800">Pase VIP</h4>
              <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                80% ATA
              </div>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>...</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>...</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>...</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <span className="text-2xl font-bold text-gray-900">$0.7</span>
              <span className="text-sm text-gray-500 ml-2">(4.5% descuento)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Formulario de Compra */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Columna Izquierda */}
        <div className="space-y-4">
          <label className="block">
            <span className="font-medium text-gray-700">Fecha de Visita</span>
            <input
              type="date"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              required
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent"
            />
          </label>

          <label className="block">
            <span className="font-medium text-gray-700">Cantidad de Entradas</span>
            <input
              type="number"
              min="1"
              max="10"
              value={cantidad}
              onChange={(e) => setCantidad(parseInt(e.target.value))}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent"
            />
          </label>

          <label className="block">
            <span className="font-medium text-gray-700">Edad del Visitante</span>
            <input
              type="number"
              min="0"
              value={edad}
              onChange={(e) => setEdad(parseInt(e.target.value))}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent"
            />
          </label>
        </div>

        {/* Columna Derecha */}
        <div className="space-y-4">
          <label className="block">
            <span className="font-medium text-gray-700">Forma de Pago</span>
            <select
              value={formaPago}
              onChange={(e) => setFormaPago(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent"
            >
              <option value="tarjeta"> Tarjeta de Crédito/Débito</option>
              <option value="efectivo"> Efectivo</option>
            </select>
          </label>

          <label className="block">
            <span className="font-medium text-gray-700">Correo Electrónico</span>
            <input
              type="email"
              value={mail}
              onChange={(e) => setMail(e.target.value)}
              required
              placeholder="ejemplo@dominio.com"
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent"
            />
          </label>

          {/* Resumen de Precio */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Subtotal:</span>
              <span className="font-semibold">
                ${(pase === "regular" ? 1.0 : 0.7 * cantidad).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold text-green-700">
              <span>Total:</span>
              <span>${(pase === "regular" ? 1.0 : 0.7 * cantidad).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Botón de Confirmación - Full Width */}
        <div className="md:col-span-2">
          <button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
          >
             Confirmar Compra
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioCompra;