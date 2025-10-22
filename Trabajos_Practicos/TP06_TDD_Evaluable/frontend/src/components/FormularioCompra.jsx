import React, { useState, useEffect } from "react";

const FormularioCompra = ({ onCompra }) => {
  const [fecha, setFecha] = useState("");
  const [cantidad, setCantidad] = useState(1);
  const [edades, setEdades] = useState([18]);
  const [pase, setPase] = useState("regular");
  const [formaPago, setFormaPago] = useState("");
  const [mail, setMail] = useState("");
  const [errores, setErrores] = useState({});
  const [camposModificados, setCamposModificados] = useState({});
  const [formularioValido, setFormularioValido] = useState(false);
  const diasCerrados = [0, 1]; // 0: Lunes, 1: Martes

  // Validar TODO el formulario en cada cambio
  useEffect(() => {
    validarFormularioCompleto();
  }, [fecha, cantidad, edades, formaPago, mail]);

  const validarFecha = (fechaString) => {
    if (!fechaString) return { valido: false, mensaje: "La fecha de visita es obligatoria" };
    
    const fechaSeleccionada = new Date(fechaString);
    const fechaActual = new Date();
    fechaActual.setHours(0, 0, 0, 0);
    const fechaSeleccionadaStr = fechaSeleccionada.toISOString().split('T')[0];
    const fechaActualStr = fechaActual.toISOString().split('T')[0]; 
    
    if (fechaSeleccionadaStr < fechaActualStr) {
      return { valido: false, mensaje: "La fecha no puede ser anterior al día actual" };
    }
    
    const diaSemana = fechaSeleccionada.getDay();
    if (diasCerrados.includes(diaSemana)) {
      const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
      return { valido: false, mensaje: `El parque está cerrado los ${dias[diaSemana]}` };
    }
    
    return { valido: true, mensaje: "" };
  };

  const validarCantidad = (cant) => {
    if (cant < 1) return { valido: false, mensaje: "Debe comprar al menos 1 entrada" };
    if (cant > 10) return { valido: false, mensaje: "Máximo 10 entradas por compra" };
    return { valido: true, mensaje: "" };
  };

  const validarEdades = (eds) => {
    for (let i = 0; i < eds.length; i++) {
      if (!eds[i] || eds[i] < 0 || eds[i] > 120) {
        return { 
          valido: false, 
          mensaje: `Edad inválida para visitante ${i + 1} (0-120)` 
        };
      }
    }
    return { valido: true, mensaje: "" };
  };

  const validarFormaPago = (fp) => {
    if (!fp) return { valido: false, mensaje: "Seleccione un método de pago" };
    return { valido: true, mensaje: "" };
  };

  const validarEmail = (email) => {
    if (!email) return { valido: false, mensaje: "El email es obligatorio" };
    if (!/\S+@\S+\.\S+/.test(email)) return { valido: false, mensaje: "Email inválido" };
    return { valido: true, mensaje: "" };
  };

  const validarFormularioCompleto = () => {
    const nuevosErrores = {};
    let esValido = true;

    const validacionFecha = validarFecha(fecha);
    if (!validacionFecha.valido) {
      nuevosErrores.fecha = validacionFecha.mensaje;
      esValido = false;
    }

    const validacionCantidad = validarCantidad(cantidad);
    if (!validacionCantidad.valido) {
      nuevosErrores.cantidad = validacionCantidad.mensaje;
      esValido = false;
    }

    const validacionEdades = validarEdades(edades);
    if (!validacionEdades.valido) {
      nuevosErrores.edades = validacionEdades.mensaje;
      esValido = false;
    }

    const validacionFormaPago = validarFormaPago(formaPago);
    if (!validacionFormaPago.valido) {
      nuevosErrores.formaPago = validacionFormaPago.mensaje;
      esValido = false;
    }

    const validacionEmail = validarEmail(mail);
    if (!validacionEmail.valido) {
      nuevosErrores.mail = validacionEmail.mensaje;
      esValido = false;
    }

    setErrores(nuevosErrores);
    setFormularioValido(esValido);
    return esValido;
  };

  const manejarCambioFecha = (valor) => {
    setCamposModificados(prev => ({ ...prev, fecha: true }));
    setFecha(valor);
    
    const validacion = validarFecha(valor);
    if (!validacion.valido) {
      setErrores(prev => ({ ...prev, fecha: validacion.mensaje }));
    } else {
      setErrores(prev => ({ ...prev, fecha: "" }));
    }
  };

  const manejarCambio = (campo, valor) => {
    setCamposModificados(prev => ({ ...prev, [campo]: true }));
    
    switch (campo) {
      case 'cantidad':
        const nuevaCantidad = parseInt(valor) || 0;
        setCantidad(nuevaCantidad);
        
        if (nuevaCantidad > edades.length) {
          const nuevasEdades = [...edades];
          for (let i = edades.length; i < nuevaCantidad; i++) {
            nuevasEdades.push(18);
          }
          setEdades(nuevasEdades);
        } else if (nuevaCantidad < edades.length) {
          setEdades(edades.slice(0, nuevaCantidad));
        }
        break;
      case 'formaPago':
        setFormaPago(valor);
        break;
      case 'mail':
        setMail(valor);
        break;
    }
  };

  const manejarCambioEdad = (index, valor) => {
    setCamposModificados(prev => ({ ...prev, edades: true }));
    const nuevasEdades = [...edades];
    nuevasEdades[index] = parseInt(valor) || 0;
    setEdades(nuevasEdades);
  };

  // NUEVA FUNCIÓN: Obtener categoría por edad
  // NUEVA FUNCIÓN: Obtener categoría por edad con precios
  const obtenerCategoriaEdad = (edad) => {
    if (edad < 4) return { 
      tipo: "Infante", 
      color: "bg-green-100 border-green-300", 
      puntoColor: "bg-green-500",
      badgeColor: "bg-green-100 text-green-800 border-green-300",
      descuento: "Entrada Gratuita",
      precio: "$0.00"
    };
    if (edad < 11) return { 
      tipo: "Niño", 
      color: "bg-blue-100 border-blue-300", 
      puntoColor: "bg-blue-500",
      badgeColor: "bg-blue-100 text-blue-800 border-blue-300",
      descuento: "50% Descuento",
      precio: pase === "regular" ? "$0.50" : "$0.35"
    };
    if (edad < 60) return { 
      tipo: "Adulto", 
      color: "bg-purple-100 border-purple-300", 
      puntoColor: "bg-purple-500",
      badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
      descuento: "Precio Completo",
      precio: pase === "regular" ? "$1.00" : "$0.70"
    };
    return { 
      tipo: "Adulto Mayor", 
      color: "bg-orange-100 border-orange-300", 
      puntoColor: "bg-orange-500",
      badgeColor: "bg-orange-100 text-orange-800 border-orange-300",
      descuento: "50% Descuento",
      precio: pase === "regular" ? "$0.50" : "$0.35"
    };
  };

  const calcularTotal = () => {
    let total = 0;
    const precioBase = pase === "regular" ? 1.0 : 0.7;
    
    edades.forEach(edad => {
      if (edad < 4) {
        // Infantes: gratis
        total += 0;
      } else if (edad < 11 || edad >= 60) {
        // Niños y Adultos Mayores: 50% descuento
        total += precioBase * 0.5;
      } else {
        // Adultos: precio completo
        total += precioBase;
      }
    });
    
    return total.toFixed(2);
  };

  const obtenerNombreDia = (fechaString) => {
    if (!fechaString) return "";
    const fecha = new Date(fechaString);
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    return dias[fecha.getDay()];
  };

  const handleSubmit = (e) => {
  e.preventDefault();
  
  if (!validarFormularioCompleto()) {
    // Marcar todos los campos como modificados para mostrar errores
    setCamposModificados({
      fecha: true,
      cantidad: true,
      edades: true,
      formaPago: true,
      mail: true
    });
    return;
  }
  
  // Crear objeto con los datos de la compra
  const compraData = {
    fecha,
    cantidad,
    edades,
    pase,
    formaPago,
    mail,
    total: calcularTotal()
  };
  
  // Llamar a la función prop onCompra
  if (onCompra) {
    onCompra(compraData);
  }
};

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-color-lime-green">
      <h2 className="text-3xl font-bold text-color-dark-green mb-8 text-center">
        Comprar Entradas
      </h2>

      {/* Selector de Tipo de Pase */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Selecciona tu Pase</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pase Regular */}
          <div 
            className={`border-2 rounded-xl p-6 cursor-pointer transition-all duration-300 ${
              pase === "regular" 
                ? "border-color-medium-green bg-color-pale-green shadow-md" 
                : "border-gray-200 hover:border-color-lime-green"
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
                <span className="w-2 h-2 bg-color-medium-green rounded-full"></span>
                <span>Acceso general al parque</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-color-medium-green rounded-full"></span>
                <span>Actividades básicas incluidas</span>
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
                <span>Acceso prioritario</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>Todas las actividades incluidas</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>Descuento especial</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <span className="text-2xl font-bold text-gray-900">$0.7</span>
              <span className="text-sm text-gray-500 ml-2">(30% descuento)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Formulario de Compra */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Columna Izquierda */}
          <div className="space-y-4">
            <label className="block">
              <span className="font-medium text-gray-700">Fecha de Visita *</span>
              <input
                type="date"
                value={fecha}
                onChange={(e) => manejarCambioFecha(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                required
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${
                  errores.fecha ? 'border-red-500 bg-red-50' : 'border-gray-300'
                }`}
              />
              {fecha && (
                <p className={`text-sm mt-1 ${
                  errores.fecha ? 'text-red-500' : 'text-color-medium-green'
                }`}>
                  {errores.fecha || `Seleccionado: ${obtenerNombreDia(fecha)}`}
                </p>
              )}
              {!fecha && camposModificados.fecha && errores.fecha && (
                <p className="text-red-500 text-sm mt-1">{errores.fecha}</p>
              )}
            </label>

            <label className="block">
              <span className="font-medium text-gray-700">Cantidad de Entradas *</span>
              <input
                type="number"
                min="1"
                max="10"
                value={cantidad}
                onChange={(e) => manejarCambio('cantidad', e.target.value)}
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${
                  errores.cantidad ? 'border-red-500 bg-red-50' : 'border-gray-300'
                }`}
              />
              {errores.cantidad && (
                <p className="text-red-500 text-sm mt-1">{errores.cantidad}</p>
              )}
              <p className="text-sm text-gray-600 mt-1">Máximo 10 entradas por compra</p>
            </label>
          </div>

          {/* Columna Derecha */}
          <div className="space-y-4">
            <label className="block">
              <span className="font-medium text-gray-700">Forma de Pago *</span>
              <select
                value={formaPago}
                onChange={(e) => manejarCambio('formaPago', e.target.value)}
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${
                  errores.formaPago ? 'border-red-500 bg-red-50' : 'border-gray-300'
                }`}
              >
                <option value="">Seleccione una opción</option>
                <option value="tarjeta"> Tarjeta de Crédito/Débito</option>
                <option value="efectivo"> Efectivo</option>
              </select>
              {errores.formaPago && (
                <p className="text-red-500 text-sm mt-1">{errores.formaPago}</p>
              )}
            </label>

            <label className="block">
              <span className="font-medium text-gray-700">Correo Electrónico *</span>
              <input
                type="email"
                value={mail}
                onChange={(e) => manejarCambio('mail', e.target.value)}
                required
                placeholder="ejemplo@dominio.com"
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${
                  errores.mail ? 'border-red-500 bg-red-50' : 'border-gray-300'
                }`}
              />
              {errores.mail && (
                <p className="text-red-500 text-sm mt-1">{errores.mail}</p>
              )}
            </label>
          </div>
        </div>

        {/* Edades de los Visitantes */}
        {/* SECCIÓN MEJORADA: Edades de los Visitantes */}
        <div className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-color-pale-green to-white">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-color-dark-green">
              Edades de los Visitantes *
            </h3>
            <div className="flex items-center gap-2 text-sm text-color-medium-green bg-white px-3 py-1 rounded-full border border-color-lime-green">
              <span className="font-medium">{cantidad}</span>
              <span>visitante{cantidad !== 1 ? 's' : ''}</span>
            </div>
          </div>

          {errores.edades && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm font-medium flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                {errores.edades}
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {edades.map((edad, index) => {
              const categoria = obtenerCategoriaEdad(edad);
              return (
                <div 
                  key={index} 
                  className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${
                    (errores.edades || !edad || edad < 0 || edad > 120) 
                      ? 'border-red-300 bg-red-50' 
                      : categoria.color
                  } hover:shadow-md`}
                >
                  {/* Header de la tarjeta */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${categoria.puntoColor}`}></div>
                      <span className="font-semibold text-sm">Visitante {index + 1}</span>
                    </div>
                    <div className={`text-xs font-medium px-2 py-1 rounded-full border ${categoria.badgeColor}`}>
                      {categoria.tipo}
                    </div>
                  </div>

                  {/* Input de edad */}
                  <div className="space-y-2">
                    <label className="block text-xs font-medium text-gray-600">
                      Edad
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="120"
                        value={edad}
                        onChange={(e) => manejarCambioEdad(index, e.target.value)}
                        className={`w-full border rounded-lg px-3 py-2 text-center font-semibold focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${
                          (errores.edades || !edad || edad < 0 || edad > 120) 
                            ? 'border-red-300 bg-white' 
                            : 'border-gray-300'
                        }`}
                        placeholder="0"
                      />
                      <span className="text-sm text-gray-500 font-medium">años</span>
                    </div>
                  </div>

                  {/* Información de precio */}
                  {edad >= 0 && edad <= 120 && edad !== "" && (
                    <div className="mt-3 p-2 bg-white rounded-lg border">
                      <div className="text-xs text-gray-600 text-center">
                        <div className="font-semibold text-color-dark-green">{categoria.descuento}</div>
                        <div className="text-color-medium-green font-bold">{categoria.precio}</div>
                      </div>
                    </div>
                  )}

                  {/* Indicador visual de edad válida */}
                  {edad >= 0 && edad <= 120 && (
                    <div className="mt-2 flex items-center justify-between text-xs">
                      <span className="text-gray-500">Edad válida</span>
                      <div className="flex items-center gap-1 text-green-500">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span>OK</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Nueva leyenda de categorías con precios */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Categorías y Precios:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              <div className="flex items-center justify-between bg-green-50 px-3 py-2 rounded-lg border border-green-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="font-medium">Infantes (0-3)</span>
                </div>
                <span className="font-bold text-green-700">GRATIS</span>
              </div>
              <div className="flex items-center justify-between bg-blue-50 px-3 py-2 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="font-medium">Niños (4-10)</span>
                </div>
                <span className="font-bold text-blue-700">50% DESC</span>
              </div>
              <div className="flex items-center justify-between bg-purple-50 px-3 py-2 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="font-medium">Adultos (11-59)</span>
                </div>
                <span className="font-bold text-purple-700">PRECIO COMPLETO</span>
              </div>
              <div className="flex items-center justify-between bg-orange-50 px-3 py-2 rounded-lg border border-orange-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="font-medium">Adultos Mayores (60+)</span>
                </div>
                <span className="font-bold text-orange-700">50% DESC</span>
              </div>
            </div>
          </div>
        </div>

        {/* Resumen de Precio */}
        <div className="bg-gradient-to-r from-color-pale-green to-color-lime-green rounded-lg p-6 border border-color-lime-green">
          <h4 className="font-semibold text-color-dark-green mb-4 text-lg">Resumen de Compra</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-700">{cantidad} entrada(s) {pase}</span>
              <span className="font-semibold">${calcularTotal()}</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold text-color-dark-green border-t border-color-medium-green pt-3">
              <span>Total a pagar:</span>
              <span className="text-xl">${calcularTotal()}</span>
            </div>
          </div>
        </div>

        {/* Botón de Confirmación */}
        <div>
          <button
            type="submit"
            disabled={!formularioValido}
            className={`w-full font-bold py-4 rounded-xl shadow-lg transition-all duration-300 transform ${
              formularioValido 
                ? 'bg-gradient-to-r from-color-medium-green to-color-light-green hover:from-color-dark-green hover:to-color-medium-green text-white hover:scale-[1.02] hover:shadow-xl' 
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            }`}
          >
            {formularioValido ? (
              <div className="flex items-center justify-center gap-2">
                <span>Continuar al Resumen</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            ) : (
              'Complete el formulario correctamente'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioCompra;