// src/App.jsx
import React, { useState } from "react";
import FormularioCompra from "./components/FormularioCompra";
import ResumenCompra from "./components/ResumenCompra";
import Confirmacion from "./components/Confirmacion";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Usuario from "./components/Usuario";
import "./App.css";


function App() {
  const [compra, setCompra] = useState(null);
  const [mensajeMail, setMensajeMail] = useState("");
  const [pasoActual, setPasoActual] = useState("formulario");

  const manejarCompraExitosa = (compraData, mailMsg) => {
    setCompra(compraData);
    setMensajeMail(mailMsg);
    setPasoActual("resumen");
  };

  const manejarConfirmacion = () => {
    // Simular envío de email y pago
    console.log("Enviando email de confirmación...");

    if (compra && compra.forma_pago === 'tarjeta') {
      console.log("Redirigiendo a Mercado Pago...");
      // Aquí simularías la redirección a Mercado Pago
      // window.location.href = "https://mercadopago.com/checkout";
    }

    // Simular éxito después de un breve delay
    setTimeout(() => {
      setPasoActual("confirmacion");
    }, 1000);
  };

  const manejarNuevaCompra = () => {
    setCompra(null);
    setMensajeMail("");
    setPasoActual("formulario");
  };

  return (
    <div className="min-h-screen flex flex-col app-background">
      <Header />

      <Usuario />

      <main className="flex-grow container mx-auto px-4 py-8">
        {/* Indicador de Pasos */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-center">
            {/* Paso 1: Formulario */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${pasoActual === "formulario"
                ? "bg-green-forest/70 border-green-forest text-white"
                : pasoActual === "resumen" || pasoActual === "confirmacion"
                  ? "bg-green-forest/40 border-green-forest/50 text-white"
                  : "bg-white text-gray-400"
                }`}>
                1
              </div>
              <span className={`ml-2 font-medium ${pasoActual === "formulario" ? "text-green-dark" : "text-green-forest"
                }`}>
                Compra
              </span>
            </div>

            <div className="w-16 h-1 bg-green-forest mx-2"></div>

            {/* Paso 2: Resumen */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${pasoActual === "resumen"
                ? "bg-green-forest/70 border-green-forest text-white"
                : pasoActual === "confirmacion"
                  ? "bg-green-forest/40 border-green-forest/50 text-white"
                  : "bg-white text-gray-400"
                }`}>
                2
              </div>
              <span className={`ml-2 font-medium ${pasoActual === "resumen" ? "text-green-dark" : pasoActual === "confirmacion" ? "text-green-forest" : "text-gray-500"
                }`}>
                Resumen
              </span>
            </div>

            <div className="w-16 h-1 bg-green-forest mx-2"></div>

            {/* Paso 3: Confirmación */}
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${pasoActual === "confirmacion"
                ? "bg-green-forest/70 border-green-forest text-white"
                : "bg-white text-gray-400"
                }`}>
                3
              </div>
              <span className={`ml-2 font-medium ${pasoActual === "confirmacion" ? "text-green-dark" : "text-gray-500"
                }`}>
                Confirmación
              </span>
            </div>
          </div>
        </div>

        <h1 className="text-4xl font-extrabold text-center text-green-dark mb-12">
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
                className="bg-gray-500 hover:bg-gray-600 text-white hover:scale-[1.02] hover:shadow-xl font-semibold py-3 px-6 rounded-lg shadow transition-all"
              >
                ← Volver Atrás
              </button>
              <button
                onClick={manejarConfirmacion}
                className="bg-green-forest/90 hover:bg-green-forest text-white hover:scale-[1.02] hover:shadow-xl font-semibold py-3 px-6 rounded-lg shadow transition-all"
              >
                Confirmar Compra →
              </button>
            </div>
          </div>
        )}

        {pasoActual === "confirmacion" && compra && mensajeMail && (
          <div className="max-w-4xl mx-auto">
            <Confirmacion mensaje={mensajeMail} compra={compra} />
            <div className="text-center mt-6">
              <button
                onClick={manejarNuevaCompra}
                className="bg-green-forest/90 hover:bg-green-forest text-white hover:scale-[1.02] hover:shadow-xl font-semibold py-3 px-8 rounded-lg shadow transition-all"
              >
                Realizar Nueva Compra
              </button>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;