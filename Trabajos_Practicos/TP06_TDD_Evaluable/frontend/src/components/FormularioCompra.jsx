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

  // Validar TODO el formulario en cada cambio --> esto es para que haga una validación en tpo real asi no hay que esperar
  // a apretar el boton para volver a corregir
  useEffect(() => {
    validarFormularioCompleto();
  }, [fecha, cantidad, edades, formaPago, mail]);

  const validarFecha = (fechaString) => {
    if (!fechaString) return { valido: false, mensaje: "La fecha de visita es obligatoria" };
    
    const fechaSeleccionada = new Date(fechaString);
    const fechaActual = new Date();
    fechaActual.setHours(0, 0, 0, 0);
    // Comparar solo las fechas sin la hora --> asi me toma bien el dia actual
    const fechaSeleccionadaStr = fechaSeleccionada.toISOString().split('T')[0];
    const fechaActualStr = fechaActual.toISOString().split('T')[0]; 
    
    if (fechaSeleccionadaStr < fechaActualStr) {
      return { valido: false, mensaje: "La fecha no puede ser anterior al día actual" };
    }
    
    const diaSemana = fechaSeleccionada.getDay();
    if (diasCerrados.includes(diaSemana)) {
      // CORRECCIÓN: Mostrar el nombre correcto del día
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

  // aca valida que la edad no sea mayor a 120 y menor a 0 
  // no esta especificado en los CA ni en los PU pero parece razonable
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

    // Validar fecha
    const validacionFecha = validarFecha(fecha);
    if (!validacionFecha.valido) {
      nuevosErrores.fecha = validacionFecha.mensaje;
      esValido = false;
    }

    // Validar cantidad
    const validacionCantidad = validarCantidad(cantidad);
    if (!validacionCantidad.valido) {
      nuevosErrores.cantidad = validacionCantidad.mensaje;
      esValido = false;
    }

    // Validar edades
    const validacionEdades = validarEdades(edades);
    if (!validacionEdades.valido) {
      nuevosErrores.edades = validacionEdades.mensaje;
      esValido = false;
    }

    // Validar forma de pago
    const validacionFormaPago = validarFormaPago(formaPago);
    if (!validacionFormaPago.valido) {
      nuevosErrores.formaPago = validacionFormaPago.mensaje;
      esValido = false;
    }

    // Validar email
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
    
    // Validación inmediata para fecha
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
        
        // Ajustar array de edades --> se debe ingresar la edad de cada visitante
        // si compro 3 entradas, debe ingresar 3 edades
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Marcar todos los campos como modificados para mostrar errores
    setCamposModificados({
      fecha: true,
      cantidad: true,
      edades: true,
      formaPago: true,
      mail: true
    });

    if (!formularioValido) {
      alert("Por favor, corrige los errores en el formulario antes de continuar.");
      return;
    }

    // Simular datos para el flujo frontend
    const usuario = { mail };
    const entradas = edades.map(edad => ({ fecha, pase, edad }));
    const compraData = { 
      entradas, 
      forma_pago: formaPago, 
      usuario,
      fechaVisita: fecha,
      cantidadEntradas: cantidad
    };

    // Crear mensaje de confirmación
    const mensajeConfirmacion = `¡Compra exitosa! Has comprado ${cantidad} entrada(s) ${pase} para el ${fecha}. ` +
      `Método de pago: ${formaPago === 'tarjeta' ? 'Tarjeta (Mercado Pago)' : 'Efectivo'}. ` +
      `Se envió confirmación a: ${mail}`;

    onCompra(compraData, mensajeConfirmacion);
  };

  const calcularTotal = () => {
    const precio = pase === "regular" ? 1.0 : 0.7;
    return (precio * cantidad).toFixed(2);
  };

  // CORRECCIÓN: Función para obtener el nombre del día
  const obtenerNombreDia = (fechaString) => {
    if (!fechaString) return "";
    const fecha = new Date(fechaString);
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    return dias[fecha.getDay()];
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-100">
      <h2 className="text-3xl font-bold text-green-700 mb-8 text-center">
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
                <span>Acceso general al parque</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
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
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent ${
                  errores.fecha ? 'border-red-500 bg-red-50' : 'border-gray-300'
                }`}
              />
              {fecha && (
                <p className={`text-sm mt-1 ${
                  errores.fecha ? 'text-red-500' : 'text-green-600'
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
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent ${
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
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent ${
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
                className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent ${
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
        <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Edades de los Visitantes *
          </h3>
          {errores.edades && (
            <p className="text-red-500 text-sm mb-3 bg-red-50 p-2 rounded border border-red-200">
              {errores.edades}
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {edades.map((edad, index) => (
              <div key={index} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Visitante {index + 1}
                </label>
                <input
                  type="number"
                  min="0"
                  max="120"
                  value={edad}
                  onChange={(e) => manejarCambioEdad(index, e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-400 focus:border-transparent ${
                    (errores.edades || !edad || edad < 0 || edad > 120) ? 'border-red-500 bg-red-50' : 'border-gray-300'
                  }`}
                  placeholder="Edad"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Resumen de Precio */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-3">Resumen de Compra</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">{cantidad} entrada(s) {pase}</span>
              <span className="font-semibold">${calcularTotal()}</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold text-green-700 border-t border-gray-300 pt-2">
              <span>Total:</span>
              <span>${calcularTotal()}</span>
            </div>
          </div>
        </div>

        {/* Botón de Confirmación */}
        <div>
          <button
            type="submit"
            disabled={!formularioValido}
            className={`w-full font-bold py-3 rounded-lg shadow-lg transition-all duration-300 transform ${
              formularioValido 
                ? 'bg-green-600 hover:bg-green-700 text-white hover:scale-105' 
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            }`}
          >
            {formularioValido ? ' Continuar al Resumen' : 'Complete el formulario correctamente'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioCompra;