import React, { useState, useEffect, useRef } from 'react';
import { UserIcon, ChevronDownIcon } from '@heroicons/react/24/solid';

const Usuario = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [dropdownRef]);

    return (

        <div className="relative" ref={dropdownRef}>
            {/* Botón del dropdown */}
            <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center focus:outline-none"
            >
                <div className="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center bg-white/10">
                    <UserIcon className="w-5 h-5 text-white" />
                </div>
                <ChevronDownIcon className="w-4 h-4 ml-1 text-white" />
            </button>

            {/* Menú desplegable */}
            {isDropdownOpen && (
                <div 
                    className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50"
                >
                    <div className="px-4 py-2 text-sm text-green-forest font-semibold">
                        Ana López
                    </div>
                    <a
                        href="#" 
                        onClick={(e) => {
                            e.preventDefault();
                            console.log("Cerrando sesión...");
                            setIsDropdownOpen(false); 
                        }}
                        className="block px-4 py-2 text-sm text-green-dark-bold hover:bg-gray-100"
                    >
                        Cerrar sesión
                    </a>
                </div>
            )}
        </div>
    );
};

export default Usuario;