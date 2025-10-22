// src/App.jsx
import React, { useState } from "react";
import FormularioCompra from "./components/FormularioCompra";
import ResumenCompra from "./components/ResumenCompra";
import Confirmacion from "./components/Confirmacion";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Usuario from "./components/Usuario";
import { useCompraEntradas } from '../hooks/useCompraEntradas'; // 💡 Importar hook para consistencia
import "./App.css";


function App() {
  const [compra, setCompra] = useState(null);
  const [mensajeMail, setMensajeMail] = useState("");
  const [pasoActual, setPasoActual] = useState("formulario");
  // 💡 NUEVOS ESTADOS: Para manejar la carga y errores en el paso 2
  const [procesandoPago, setProcesandoPago] = useState(false);
  const [error, setError] = useState(null);

  // Se mantiene aquí, aunque procesarPagoFinal no esté implementado en el hook
  // La simulación se realiza en manejarConfirmacion.

  const manejarCompraExitosa = (compraData, mailMsg) => {
    setCompra(compraData);
    setMensajeMail(mailMsg);
    setPasoActual("resumen");
    setError(null); // Limpiar cualquier error anterior de formulario
  };
  
  const manejarVolverAFormulario = () => {
    setPasoActual("formulario");
    setError(null);
  };

  // 💡 MODIFICACIÓN CLAVE: Lógica de confirmación asíncrona
 const manejarConfirmacion = async () => {
    setProcesandoPago(true);
    setError(null);
    
    // 💡 CONSOLE.LOG 6: Inicio del proceso de confirmación
    console.log("6. App: Iniciando proceso de confirmación de pago/reserva."); 

    try {
      if (!compra) {
          // Si compra es null, el flujo está roto
          console.error("Error: Objeto compra es nulo."); 
        throw new Error("Error interno: Faltan datos de la compra para confirmar.");
      }
      
      // 🚨 PUNTO CLAVE DE DEPURACIÓN 🚨
      console.log(`Método de pago detectado: ${compra.formaPago}`); 

      // Usa la propiedad CORRECTA: 'formaPago'
      if (compra.formaPago === 'tarjeta') { 
        console.log(`7. App: [TARJETA] Procesando pago de compra ID ${compra.id}. Simulación de 2s...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        console.log("8. App: [TARJETA] Pago procesado exitosamente (simulado).");
        
      } else if (compra.formaPago === 'efectivo') {
        console.log(`7. App: [EFECTIVO] Confirmando reserva ID ${compra.id}. Simulación de 1s...`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log("8. App: [EFECTIVO] Reserva confirmada exitosamente (simulado).");
      }

      setPasoActual("confirmacion");
      
    } catch (err) {
      console.error('Error en confirmación:', err);
      setError(err.message || "Error al procesar el pago. Por favor, intente nuevamente.");
    } finally {
      setProcesandoPago(false);
    }
  };

  const manejarNuevaCompra = () => {
    setCompra(null);
    setMensajeMail("");
    setPasoActual("formulario");
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col app-background">
      <Header />

      <Usuario />

      <main className="flex-grow container mx-auto px-4 py-8">
        {/* Indicador de Pasos */}
        {/* (Se mantiene el estilo de pasos) */}
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
        
        {/* 💡 MOSTRAR ERROR GLOBAL (Añadido) */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center justify-between gap-2 text-red-600">
              <span className="font-medium">{error}</span>
                {pasoActual === 'resumen' && (
                    <button onClick={manejarVolverAFormulario} className="text-sm underline">
                        Volver a editar
                    </button>
                )}
            </div>
          </div>
        )}


        <h1 className="text-4xl font-extrabold text-center text-green-dark mb-12">
          EcoHarmony Park - Entradas
        </h1>

        {/* Contenido Dinámico */}
        {pasoActual === "formulario" && (
          <FormularioCompra onCompra={manejarCompraExitosa} />
        )}

        {pasoActual === "resumen" && compra && (
          <div className="max-w-4xl mx-auto">
            <ResumenCompra 
                compra={compra} 
                onConfirmar={manejarConfirmacion}
                onEditar={manejarVolverAFormulario}
                procesandoPago={procesandoPago} // 💡 Pasar estado de carga
            />
            <div className="flex gap-4 justify-center mt-6">
              <button
                onClick={manejarVolverAFormulario}
                className="bg-gray-500 hover:bg-gray-600 text-white hover:scale-[1.02] hover:shadow-xl font-semibold py-3 px-6 rounded-lg shadow transition-all"
                disabled={procesandoPago}
              >
                ← Volver Atrás
              </button>
              <button
                onClick={manejarConfirmacion}
                disabled={procesandoPago}
                className="bg-green-forest/90 hover:bg-green-forest text-white hover:scale-[1.02] hover:shadow-xl font-semibold py-3 px-6 rounded-lg shadow transition-all flex items-center justify-center gap-2"
              >
                {/* 💡 INDICADOR DE CARGA */}
                {procesandoPago ? (
                    <>
                        <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Procesando...
                    </>
                ) : (
                    `Confirmar Compra →`
                )}
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

