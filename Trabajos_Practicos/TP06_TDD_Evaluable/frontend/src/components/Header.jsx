import React from "react";

const Header = () => {
  return (
    <header className="bg-green-700 text-white py-4 shadow-md">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-4">
        <h1 className="text-2xl font-bold tracking-wide">EcoHarmony Park</h1>
        <nav>
          <ul className="flex gap-8">
            <li className="hover:text-green-200 cursor-pointer transition">Inicio</li>
            <li className="hover:text-green-200 cursor-pointer transition">Entradas</li>
            <li className="hover:text-green-200 cursor-pointer transition">Actividades</li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
