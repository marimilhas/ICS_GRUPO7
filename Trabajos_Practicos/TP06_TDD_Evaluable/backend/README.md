# Comandos para ejecutar desde "backend": 

1. Crear un entorno virtual: python -m venv venv
2. Activar el entorno virtual: venv\Scripts\activate    // Si salta un error de permisos ejecutar esto: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass y volver a ejecutar el paso dos.
3. Instalar dependencias: pip install -r requirements.txt
4. Correr tests específicos: pytest entradas/tests/test_comprar_entradas.py -v        // Para ver solo los test que pasan: pytest -v | findstr PASSED
5. Luego, para salir del entorno virtual: deactivate

