import React, { useState } from "react";
import logo from "../assets/logo_reducido.png";
import "../css/header.css";

const Header = () => {
  const [menuAbierto, setMenuAbierto] = useState(false);

  return (
    <header className="text-white py-4 shadow-md" id="header">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-4">

        <div className="flex items-center gap-2">
          <img
            src={logo}
            alt="EcoHarmony Park logo"
            className="w-12 h-12 rounded-lg"
          />
          <h1 className="text-xl sm:text-2xl font-bold tracking-wide whitespace-nowrap">
            EcoHarmony Park
          </h1>
        </div>

        {/* Botón de menú para celulares */}
        <button
          className="md:hidden focus:outline-none"
          onClick={() => setMenuAbierto(!menuAbierto)}
        >
          {menuAbierto ? (
            <span className="text-3xl">&times;</span>
          ) : (
            <span className="text-3xl">&#9776;</span>
          )}
        </button>


        {/* Barra de navegación para PC */}
        <nav className="hidden md:block">
          <ul className="flex gap-8 text-lg font-semibold">
            <li className="cursor-pointer transition navegacion">Inicio</li>
            <li className="cursor-pointer transition navegacion">Entradas</li>
            <li className="cursor-pointer transition navegacion">Actividades</li>
          </ul>
        </nav>
      </div>

      {/* Menú desplegable para celulares */}
      {menuAbierto && (
        <nav className="md:hidden bg-green-forest text-white mt-2 shadow-lg rounded-lg mx-4">
          <ul className="flex flex-col items-center gap-3 py-4 text-lg font-semibold">
            <li className="cursor-pointer navegacion">Inicio</li>
            <li className="cursor-pointer navegacion">Entradas</li>
            <li className="cursor-pointer navegacion">Actividades</li>
          </ul>
        </nav>
      )}

    </header>
  );
};

export default Header;
