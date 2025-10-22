Comandos para ejecutar desde "backend": 
1. python -m venv venv
2. venv\Scripts\activate    // Si salta un error de permisos ejecutar esto: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass y volver a ejecutar el paso 2
3. pip install -r requirements.txt
4. pytest entradas/tests/test_comprar_entradas.py -v        // Para ver solo los test que pasan: pytest -v | findstr PASSED
