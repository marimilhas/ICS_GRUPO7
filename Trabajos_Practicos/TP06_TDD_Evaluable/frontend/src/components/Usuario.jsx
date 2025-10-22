import { UserIcon } from '@heroicons/react/24/solid';

const Usuario = () => {
    return (
        <>
            <div className="flex items-center justify-end mt-2 mr-2">
                <div className="w-8 h-8 rounded-full border-2 border-green-forest flex items-center justify-center bg-green-forest/10 mr-2">
                    <UserIcon className="w-6 h-6 text-green-forest" />
                </div>
                <span className="text-green-forest cursor-pointer">
                    Ana López
                    <span className="text-green-dark text-bold cursor-pointer"> | Cerrar sesión</span>
                </span>
            </div>
        </>
    );
}

export default Usuario;