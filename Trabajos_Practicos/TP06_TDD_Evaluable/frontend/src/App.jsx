// src/App.jsx
import React, { useState } from "react";
import FormularioCompra from "./components/FormularioCompra";
import ResumenCompra from "./components/ResumenCompra";
import Confirmacion from "./components/Confirmacion";
import Header from "./components/Header";
import Footer from "./components/Footer";

function App() {
  const [compra, setCompra] = useState(null);
  const [mensajeMail, setMensajeMail] = useState("");
  const [pasoActual, setPasoActual] = useState("formulario"); // "formulario", "resumen", "confirmacion"

  const manejarCompraExitosa = (compraData, mailMsg) => {
    setCompra(compraData);
    setMensajeMail(mailMsg);
    setPasoActual("resumen");
  };

  const manejarConfirmacion = () => {
    setPasoActual("confirmacion");
  };

  const manejarNuevaCompra = () => {
    setCompra(null);
    setMensajeMail("");
    setPasoActual("formulario");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-green-50 to-emerald-100 text-gray-800">
      {/* Encabezado */}
      <Header />

      {/* Contenido central */}
      <main className="flex-grow container mx-auto px-4 py-8">
        {/* Indicador de Pasos */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-center">
            {/* Paso 1: Formulario */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                pasoActual === "formulario" 
                  ? "bg-green-600 border-green-700 text-white" 
                  : pasoActual === "resumen" || pasoActual === "confirmacion"
                  ? "bg-green-500 border-green-600 text-white"
                  : "bg-white border-green-400 text-green-600"
              }`}>
                1
              </div>
              <span className={`ml-2 font-medium ${
                pasoActual === "formulario" ? "text-green-700" : "text-green-600"
              }`}>
                Compra
              </span>
            </div>

            {/* Línea conectadora */}
            <div className="w-16 h-1 bg-green-300 mx-2"></div>

            {/* Paso 2: Resumen */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                pasoActual === "resumen" 
                  ? "bg-green-600 border-green-700 text-white" 
                  : pasoActual === "confirmacion"
                  ? "bg-green-500 border-green-600 text-white"
                  : "bg-white border-green-300 text-gray-400"
              }`}>
                2
              </div>
              <span className={`ml-2 font-medium ${
                pasoActual === "resumen" ? "text-green-700" : "text-gray-500"
              }`}>
                Resumen
              </span>
            </div>

            {/* Línea conectadora */}
            <div className="w-16 h-1 bg-green-300 mx-2"></div>

            {/* Paso 3: Confirmación */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                pasoActual === "confirmacion" 
                  ? "bg-green-600 border-green-700 text-white" 
                  : "bg-white border-green-300 text-gray-400"
              }`}>
                3
              </div>
              <span className={`ml-2 font-medium ${
                pasoActual === "confirmacion" ? "text-green-700" : "text-gray-500"
              }`}>
                Confirmación
              </span>
            </div>
          </div>
        </div>

        {/* Título Principal */}
        <h1 className="text-4xl font-extrabold text-center text-green-800 mb-12 flex items-center justify-center gap-3">
          EcoHarmony Park - Entradas
        </h1>

        {/* Contenido Dinámico */}
        {pasoActual === "formulario" && (
          <FormularioCompra onCompra={manejarCompraExitosa} />
        )}

        {pasoActual === "resumen" && compra && (
          <div className="max-w-4xl mx-auto">
            <ResumenCompra compra={compra} />
            <div className="flex gap-4 justify-center mt-6">
              <button
                onClick={() => setPasoActual("formulario")}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg shadow transition-all"
              >
                ← Volver Atrás
              </button>
              <button
                onClick={manejarConfirmacion}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow transition-all"
              >
                Confirmar Compra →
              </button>
            </div>
          </div>
        )}

        {pasoActual === "confirmacion" && compra && mensajeMail && (
          <div className="max-w-4xl mx-auto">
            <Confirmacion mensaje={mensajeMail} />
            <div className="text-center mt-6">
              <button
                onClick={manejarNuevaCompra}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg shadow transition-all"
              >
                 Realizar Nueva Compra
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Pie */}
      <Footer />
    </div>
  );
}

export default App;