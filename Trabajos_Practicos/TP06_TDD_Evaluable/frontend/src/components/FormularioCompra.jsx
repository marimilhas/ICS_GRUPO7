import React, { useState, useEffect } from "react";
import { entradasService } from "../services/entradasService.js";
import { useCompraEntradas } from '../hooks/useCompraEntradas.js';
import "../css/form.css";

const FormularioCompra = ({ onCompra }) => {
  const [fecha, setFecha] = useState("");
  const [cantidad, setCantidad] = useState(1);
  const [entradas, setEntradas] = useState([{ edad: 18, pase: "regular" }]);
  const [formaPago, setFormaPago] = useState("");
  const [mail, setMail] = useState("");
  const [errores, setErrores] = useState({});
  const [camposModificados, setCamposModificados] = useState({});
  const [formularioValido, setFormularioValido] = useState(false);

  const [pasesDisponibles, setPasesDisponibles] = useState([]);
  const [errorCargaPases, setErrorCargaPases] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorBackend, setErrorBackend] = useState(null); // 💡 Estado para errores del backend en el paso 1

  const diasCerrados = [1]; // 1: Lunes
  const diasFestivos = [
    { dia: 25, mes: 12 }, // 25 de diciembre
    { dia: 1, mes: 1 }, // 1 de enero
  ];

  // Lógica de carga de pases
  useEffect(() => {
    const cargarPases = async () => {
      console.log("1. Formulario: Intentando cargar pases desde el backend...");
      try {
        const response = await entradasService.getPases();
        setPasesDisponibles(response.data);
        setErrorCargaPases(null); 
      } catch (err) {
        console.error('Error cargando pases:', err);
        setErrorCargaPases("Error al cargar los tipos de pase disponibles. Se usarán precios predeterminados.");
      }
    };
    cargarPases();
  }, []);

  // Validar todo el formulario en cada cambio
  useEffect(() => {
    if (Object.keys(camposModificados).length > 0 || Object.keys(errores).length > 0) {
      validarFormularioCompleto();
    }
  }, [fecha, cantidad, entradas, formaPago, mail, camposModificados]);

  // --- Lógica de Validación (Interna) ---
  const validarFecha = (fechaString) => {
    if (!fechaString) return { valido: false, mensaje: "La fecha de visita es obligatoria" };
    const fechaActual = new Date();
    fechaActual.setHours(0, 0, 0, 0);

    const [anioStr, mesStr, diaStr] = fechaString.split('-');
    const dia = parseInt(diaStr, 10);
    const mes = parseInt(mesStr, 10);
    const fechaSeleccionada = new Date(parseInt(anioStr), mes - 1, dia);

    if (fechaSeleccionada < fechaActual) {
      return { valido: false, mensaje: "La fecha no puede ser anterior al día actual" };
    }

    const diaSemana = fechaSeleccionada.getDay();
    if (diasCerrados.includes(diaSemana)) {
      const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
      return { valido: false, mensaje: `El parque está cerrado los ${dias[diaSemana]}` };
    }

    const esFestivo = diasFestivos.some(f => f.dia === dia && f.mes === mes);
    if (esFestivo) {
      return { valido: false, mensaje: "El parque está cerrado en días festivos" };
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
      if (eds[i] === null || eds[i] === undefined || eds[i] < 0 || eds[i] > 120) {
        return { valido: false, mensaje: `Edad inválida (0-120)` };
      }
    }
    return { valido: true, mensaje: "" };
  };

  const validarFormaPago = (fp) => {
    if (!fp || fp === "") {
      return { valido: false, mensaje: "Seleccione un método de pago" };
    }
    return { valido: true, mensaje: "" };
  };

  const validarEmail = (email) => {
    if (!email) return { valido: false, mensaje: "El email es obligatorio" };
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { valido: false, mensaje: "Email inválido" };
    return { valido: true, mensaje: "" };
  };

  const validarFormularioCompleto = () => {
    const nuevosErrores = {};
    let esValido = true;
    
    const validacionFecha = validarFecha(fecha);
    if (!validacionFecha.valido) { nuevosErrores.fecha = validacionFecha.mensaje; esValido = false; }

    const validacionCantidad = validarCantidad(cantidad);
    if (!validacionCantidad.valido) { nuevosErrores.cantidad = validacionCantidad.mensaje; esValido = false; }

    const edades = entradas.map(e => e.edad);
    const validacionEdades = validarEdades(edades);
    if (!validacionEdades.valido) { 
      const cantidadErrores = edades.filter(edad => edad === null || edad === undefined || edad < 0 || edad > 120).length;
      nuevosErrores.edades = { mensajeBase: validacionEdades.mensaje, cantidad: cantidadErrores };
      esValido = false;
    }

    const validacionFormaPago = validarFormaPago(formaPago);
    if (!validacionFormaPago.valido) { nuevosErrores.formaPago = validacionFormaPago.mensaje; esValido = false; }

    const validacionEmail = validarEmail(mail);
    if (!validacionEmail.valido) { nuevosErrores.mail = validacionEmail.mensaje; esValido = false; }

    setErrores(nuevosErrores);
    setFormularioValido(esValido);
    return esValido;
  };
  // --- Fin Lógica de Validación (Interna) ---
  
  // Handlers
  const manejarCambioFecha = (valor) => { setCamposModificados(prev => ({ ...prev, fecha: true })); setFecha(valor); };
  const manejarCambio = (campo, valor) => {
    setCamposModificados(prev => ({ ...prev, [campo]: true }));
    switch (campo) {
      case 'cantidad':
        const nuevaCantidad = parseInt(valor) || 0;
        setCantidad(nuevaCantidad);
        const nuevasEntradas = [...entradas];
        if (nuevaCantidad > entradas.length) {
          for (let i = entradas.length; i < nuevaCantidad; i++) {
            nuevasEntradas.push({ edad: 18, pase: "regular" });
          }
        } else if (nuevaCantidad < entradas.length) {
          nuevasEntradas.length = nuevaCantidad;
        }
        setEntradas(nuevasEntradas);
        break;
      case 'formaPago': setFormaPago(valor); break;
      case 'mail': setMail(valor); break;
    }
  };
  const manejarCambioEntrada = (index, campo, valor) => {
    setCamposModificados(prev => ({ ...prev, entradas: true }));
    const nuevasEntradas = [...entradas];
    if (campo === 'edad') { nuevasEntradas[index].edad = parseInt(valor) || 0; } 
    else if (campo === 'pase') { nuevasEntradas[index].pase = valor; }
    setEntradas(nuevasEntradas);
  };
  // Lógica de cálculo de precios (se mantiene para el resumen local)
  const obtenerCategoriaEdad = (edad, pase) => {
    const paseData = pasesDisponibles.find(p => p.nombre?.toLowerCase().includes(pase.toLowerCase()));
    const precioBase = paseData?.precio || (pase.toLowerCase() === "regular" ? 5000 : 10000);

    if (edad < 3) return { tipo: "Infante", color: "bg-green-light/15 border-green-light", puntoColor: "bg-green-light", badgeColor: "bg-green-light/5 text-green-light-bold text-semibold border-green-light-bold", descuento: "Entrada Gratuita", precio: "$0,00", precioNumerico: 0 };
    if (edad < 10 || edad > 60) return { tipo: edad < 10 ? "Niño" : "Adulto Mayor", color: edad < 10 ? "bg-green-medium/15 border-green-medium" : "bg-green-dark/15 border-green-dark", puntoColor: edad < 10 ? "bg-green-medium" : "bg-green-dark", badgeColor: edad < 10 ? "bg-green-medium/5 text-green-medium-bold border-green-medium-bold" : "bg-green-dark/5 text-green-dark border-green-dark", descuento: "50% Descuento", precio: `$${(precioBase * 0.5).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, precioNumerico: precioBase * 0.5 };
    return { tipo: "Adulto", color: "bg-green-forest/15 border-green-forest", puntoColor: "bg-green-forest", badgeColor: "bg-green-forest/5 text-green-forest-bold border-green-forest-bold", descuento: "Precio Completo", precio: `$${precioBase.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, precioNumerico: precioBase };
  };
  const calcularTotalNumerico = () => {
    return entradas.reduce((total, e) => total + obtenerCategoriaEdad(e.edad, e.pase).precioNumerico, 0);
  };
  const calcularTotal = () => {
    return calcularTotalNumerico().toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };
  const obtenerNombreDia = (fechaString) => {
    if (!fechaString) return "";
    const fecha = new Date(fechaString.replace(/-/g, "/"));
    const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    return dias[fecha.getDay()];
  };

  // ==========================================================
  // 🚀 MODIFICACIÓN CLAVE: Lógica de Validación de Backend en Submit
  // ==========================================================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorBackend(null); // Limpiar error previo
    
    // 1. Validar el formulario localmente
    if (!validarFormularioCompleto()) {
      setCamposModificados({ fecha: true, cantidad: true, entradas: true, formaPago: true, mail: true });
      return;
    }
    
    setLoading(true);

    try {
      // Preparamos los datos mínimos para enviar al endpoint de VALIDACIÓN
      const datosValidacion = {
        fecha_visita: fecha,
        cantidad: cantidad,
        visitantes: entradas.map(entrada => ({
          // Nota: El backend espera 'tipo_pase' capitalizado
          edad: entrada.edad,
          tipo_pase: entrada.pase.charAt(0).toUpperCase() + entrada.pase.slice(1), 
        })),
        // Nota: El backend espera 'forma_pago' capitalizado (ej. 'Tarjeta')
        forma_pago: formaPago.charAt(0).toUpperCase() + formaPago.slice(1), 
        usuario: {
            email: mail,
            nombre: "Cliente",
            esta_registrado: true
        }
      };

      console.log("4. Formulario: Enviando datos a endpoint de VALIDACIÓN...");

      // 2. Llamada al nuevo endpoint de validación
      const response = await entradasService.validateCompra(datosValidacion);
      const montoValidado = response.data.monto_total_validado; // Obtener el monto total validado por el backend

      console.log("5. Formulario: Validación de backend exitosa. Monto total:", montoValidado);
      
      // 3. Si la validación es exitosa, pasamos los datos completos al componente App
      const compraPreliminar = {
        fecha: fecha,
        cantidad: cantidad,
        entradas: entradas.map(entrada => ({
          ...entrada,
          precioNumerico: obtenerCategoriaEdad(entrada.edad, entrada.pase).precioNumerico
        })),
        formaPago: formaPago,
        mail: mail,
        // Usamos el monto validado por el backend
        total: montoValidado.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }), 
        totalNumerico: montoValidado // Lo guardamos para la confirmación final
      };

      if (onCompra) {
        // Llama a manejarDatosCompra en App.jsx para pasar al resumen
        onCompra(compraPreliminar);
      }

    } catch (err) {
      console.error('Error en el formulario al validar con backend:', err);
      
      const errorMsg = err.response?.data?.error || err.response?.data?.mensaje || err.response?.data || err.message || "Error desconocido al validar la compra.";
      
      // Intentar extraer el mensaje de error si el cuerpo es una cadena simple
      let finalErrorMsg = typeof errorMsg === 'object' && errorMsg !== null ? JSON.stringify(errorMsg) : String(errorMsg);
      if (err.response?.data?.error) { // Si el error viene envuelto en {error: "..."}
          finalErrorMsg = err.response.data.error;
      } else if (typeof err.response?.data === 'string' && err.response.data.includes('Forma de pago')) {
          finalErrorMsg = err.response.data; // Si Django devuelve la excepción directamente como texto
      }
      
      setErrorBackend(finalErrorMsg); // Mostrar el error del backend
    } finally {
      setLoading(false);
    }
  };
  // --- Fin Modificación Clave ---

  // Para mostrar el mini resumen de compra antes de continuar
  const entradasAgrupadas = entradas.reduce((acc, entrada) => {
    const categoria = obtenerCategoriaEdad(entrada.edad, entrada.pase).tipo;
    const key = `${entrada.pase} - ${categoria}`;
    if (!acc[key]) { acc[key] = { pase: entrada.pase, categoria, cantidad: 0, precioUnitario: obtenerCategoriaEdad(entrada.edad, entrada.pase).precioNumerico }; }
    acc[key].cantidad += 1;
    return acc;
  }, {});
  const entradasRender = Object.values(entradasAgrupadas);


  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-green-light">
      <h2 className="text-3xl font-bold text-green-dark mb-8 text-center">Comprar Entradas</h2>

      {/* Mostrar error de carga de pases (Backend GetPases) */}
      {errorCargaPases && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-700 font-medium">{errorCargaPases}</p>
        </div>
      )}

      {/* 💡 Mostrar error del backend (Validación Post) */}
      {errorBackend && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 font-medium flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            {errorBackend}
          </p>
        </div>
      )}

      {/* Información importante sobre horarios */}
      <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div className="flex flex-col items-center text-center">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-[#3DA35D] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <h3 className="font-semibold text-[#3DA35D] text-lg">Información importante</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
            <div className="flex items-center justify-center gap-2 text-green-700">
              <svg className="w-4 h-4 text-[#3DA35D] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span><span className="font-medium">Horario:</span> 9:00 - 19:00 hrs</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-green-700">
              <svg className="w-4 h-4 text-[#3DA35D] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span><span className="font-medium">Lunes:</span> Cerrado</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-green-700">
              <svg className="w-4 h-4 text-[#3DA35D] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span><span className="font-medium">25 Dic / 1 Ene:</span> Cerrado</span>
            </div>
          </div>
        </div>
      </div>

      {/* Formulario de Compra */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <label className="block">
              <span className="font-medium text-gray-700">Fecha de Visita *</span>
              <input type="date" value={fecha} onChange={(e) => manejarCambioFecha(e.target.value)} min={new Date().toISOString().split('T')[0]} required className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${errores.fecha ? 'border-red-500 bg-red-50' : 'border-gray-300'}`} />
              <div className="min-h-[20px] mt-1">{errores.fecha ? (<p className="text-red-500 text-sm">{errores.fecha}</p>) : fecha ? (<p className="text-color-medium-green text-sm">Seleccionado: {obtenerNombreDia(fecha)}</p>) : null}</div>
            </label>
            <label className="block">
              <span className="font-medium text-gray-700">Cantidad de Entradas (Máximo 10 por compra) *</span>
              <input type="number" min="1" max="10" value={cantidad} onChange={(e) => manejarCambio('cantidad', e.target.value)} className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${errores.cantidad ? 'border-red-500 bg-red-50' : 'border-gray-300'}`} />
              <div className="min-h-[20px] mt-1">{errores.cantidad && (<p className="text-red-500 text-sm">{errores.cantidad}</p>)}</div>
            </label>
          </div>
          <div className="space-y-4">
            <label className="block">
              <span className="font-medium text-gray-700">Forma de Pago *</span>
              <select value={formaPago} onChange={(e) => manejarCambio('formaPago', e.target.value)} className={`mt-1 w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${errores.formaPago ? 'border-red-500 bg-red-50' : 'border-gray-300'}`} required>
                <option value="">Seleccione una forma de pago</option>
                <option value="tarjeta"> Tarjeta de Crédito/Débito</option>
                <option value="efectivo"> Efectivo</option>
              </select>
              <div className="min-h-[20px] mt-1">{errores.formaPago && (<p className="text-red-500 text-sm">{errores.formaPago}</p>)}</div>
            </label>
            <label className="block">
              <span className="font-medium text-gray-700">Correo Electrónico *</span>
              <input type="email" value={mail} onChange={(e) => manejarCambio('mail', e.target.value)} required placeholder="ejemplo@dominio.com" className={`mt-1 w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${errores.mail ? 'border-red-500 bg-red-50' : 'border-gray-300'}`} />
              <div className="min-h-[20px] mt-1">{errores.mail && (<p className="text-red-500 text-sm">{errores.mail}</p>)}</div>
            </label>
          </div>
        </div>

        {/* Info sobre tipos de Pase, categorías y precios (Contenido completo para visualización) */}
        <div className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-color-pale-green to-white">
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Tipos de Pase y precios</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={"border-2 rounded-xl p-6 transition-all duration-300 border-green-medium bg-green-pale bg-opacity-30 shadow-md"}>
                <div className="flex justify-between items-start mb-4"><h4 className="text-lg font-bold text-gray-800">Pase Regular</h4></div>
                <div className="space-y-2 text-sm text-gray-600"><div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-medium rounded-full"></span><span>Acceso general al parque</span></div><div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-medium rounded-full"></span><span>Actividades básicas incluidas</span></div></div>
                <div className="mt-4 pt-4 border-t border-green-medium"><span className="text-2xl font-bold text-gray-900">${pasesDisponibles.find(p => p.nombre?.toLowerCase().includes('regular'))?.precio?.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '5.000,00'}</span><span className="text-sm text-gray-500 ml-2">por persona</span></div>
              </div>
              <div className={"border-2 rounded-xl p-6 transition-all duration-300 border-green-forest bg-green-light bg-opacity-25 shadow-md"}>
                <div className="flex justify-between items-start mb-4"><h4 className="text-lg font-bold text-gray-800">Pase VIP</h4></div>
                <div className="space-y-2 text-sm text-gray-600"><div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-forest rounded-full"></span><span>Acceso prioritario</span></div><div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-forest rounded-full"></span><span>Todas las actividades incluidas</span></div></div>
                <div className="mt-4 pt-4 border-t border-green-medium"><span className="text-2xl font-bold text-gray-900">${pasesDisponibles.find(p => p.nombre?.toLowerCase().includes('vip'))?.precio?.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '10.000,00'}</span><span className="text-sm text-gray-500 ml-2">por persona</span></div>
              </div>
            </div>
          </div>
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Categorías</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              <div className="flex items-center justify-between bg-green-light bg-opacity-15 px-3 py-2 rounded-lg border border-green-light"><div className="flex items-center gap-2"><div className="w-2 h-2 bg-green-light rounded-full"></div><span className="font-medium">Infantes (0-3)</span></div><span className="font-bold text-green-light-bold">GRATIS</span></div>
              <div className="flex items-center justify-between bg-green-medium bg-opacity-15 px-3 py-2 rounded-lg border border-green-medium"><div className="flex items-center gap-2"><div className="w-2 h-2 bg-green-medium rounded-full"></div><span className="font-medium">Niños (4-10)</span></div><span className="font-bold text-green-medium-bold">50% DESC</span></div>
              <div className="flex items-center justify-between bg-green-forest bg-opacity-15 px-3 py-2 rounded-lg border border-green-forest"><div className="flex items-center gap-2"><div className="w-2 h-2 bg-green-forest rounded-full"></div><span className="font-medium">Adultos (11-59)</span></div><span className="font-bold text-green-forest-bold">PRECIO COMPLETO</span></div>
              <div className="flex items-center justify-between bg-green-dark bg-opacity-15 px-3 py-2 rounded-lg border border-green-dark"><div className="flex items-center gap-2"><div className="w-2 h-2 bg-green-dark rounded-full"></div><span className="font-medium">Adultos Mayores (60+)</span></div><span className="font-bold text-green-dark-bold">50% DESC</span></div>
            </div>
          </div>
        </div>

        {/* Edades de los Visitantes y tipos de pase de cada entrada (Contenido completo para visualización) */}
        <div className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-color-pale-green to-white">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
            <h3 className="text-xl font-semibold">Edades de los Visitantes *</h3>
            <div className="flex items-center gap-2 text-sm bg-white px-3 py-1 rounded-full border self-start md:self-auto"><span className="font-medium">{cantidad}</span><span>visitante{cantidad !== 1 ? 's' : ''}</span></div>
          </div>
          {errores.edades && typeof errores.edades === 'object' && (<div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"><p className="text-red-600 text-sm font-medium flex items-center gap-2"><svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" /></svg>{errores.edades.cantidad === 1 ? 'Edad inválida' : `Existen ${errores.edades.cantidad} edades inválidas`} (0-120)</p></div>)}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {entradas.map((entrada, index) => {
              const categoria = obtenerCategoriaEdad(entrada.edad, entrada.pase);
              return (
                <div key={index} className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${(entrada.edad === null || entrada.edad === undefined || entrada.edad < 0 || entrada.edad > 120) ? 'border-red-300 bg-red-50' : categoria.color} hover:shadow-md`}>
                  <div className="flex items-center justify-between mb-3"><div className="flex items-center gap-2"><div className={`w-3 h-3 rounded-full ${(entrada.edad === null || entrada.edad === undefined || entrada.edad < 0 || entrada.edad > 120) ? 'bg-red-500' : categoria.puntoColor}`}></div><span className="font-semibold text-sm">Visitante {index + 1}</span></div><div className={`text-xs font-medium px-2 py-1 rounded-full border ${categoria.badgeColor}`}>{categoria.tipo}</div></div>
                  <div className="flex items-center justify-between gap-2">
                    <label className="text-xs font-medium text-gray-600 text-left">Edad: </label>
                    <div className="flex items-center gap-2 flex-1">
                      <input type="number" min="0" max="120" value={entrada.edad} onChange={(e) => manejarCambioEntrada(index, 'edad', e.target.value)} className={`w-full border rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-color-medium-green focus:border-transparent ${(entrada.edad === null || entrada.edad === undefined || entrada.edad < 0 || entrada.edad > 120) ? 'border-red-300 bg-white' : 'border-gray-300'}`} placeholder="0" />
                      <span className="text-sm text-gray-500 font-medium">años</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between gap-2 mt-2">
                    <label className="text-xs font-medium text-gray-600 text-left">Tipo de pase: </label>
                    <select value={entrada.pase} onChange={(e) => manejarCambioEntrada(index, 'pase', e.target.value)} className="flex-1 border rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-color-medium-green focus:border-transparent">
                      <option value="regular">Regular</option><option value="VIP">VIP</option>
                    </select>
                  </div>
                  {entrada.edad >= 0 && entrada.edad <= 120 && entrada.edad !== "" && (<div className="mt-3 p-2 bg-white rounded-lg border"><div className="text-xs text-gray-600 text-center"><div className="font-semibold text-green-dark">{categoria.descuento}</div><div className="text-green-forest font-bold">{categoria.precio}</div></div></div>)}
                  <div className="mt-2 flex items-center justify-between text-xs">{entrada.edad >= 0 && entrada.edad <= 120 ? (<><span className="text-gray-500">Edad válida</span><div className="flex items-center gap-1 text-green-500"><svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg><span>OK</span></div></>) : (<span className="text-red-500 font-medium">Edad inválida</span>)}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Resumen de Precio (Contenido completo para visualización) */}
        <div className="bg-gradient-to-r from-green-pale/10 to-green-light/10 rounded-lg p-6 border border-green-forest">
          <h4 className="font-semibold text-color-dark-green mb-4 text-lg">Resumen de Compra Local</h4>
          <div className="space-y-3">
            <div className="space-y-1 w-full">
              {entradasRender.map((item, index) => (<div key={index} className="flex justify-between w-full"><span className="text-left flex-1">{item.cantidad} entrada(s) {item.pase} - {item.categoria}</span><span className="font-semibold text-right w-24">${(item.cantidad * item.precioUnitario).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>))}
            </div>
            <div className="flex justify-between items-center text-lg font-bold text-green-dark border-t border-green-forest pt-3"><span>Total estimado:</span><span className="text-xl">${calcularTotal()}</span></div>
          </div>
        </div>


        {/* Botón de Continuar */}
        <div>
          <button
            type="submit"
            disabled={!formularioValido || loading}
            className={`w-full font-bold py-4 rounded-xl shadow-lg transition-all duration-300 transform ${formularioValido && !loading
              ? 'bg-green-forest/90 hover:bg-green-forest text-white hover:scale-[1.02] hover:shadow-xl'
              : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Validando datos...</span>
              </div>
            ) : formularioValido ? (
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
