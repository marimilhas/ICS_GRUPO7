⚙️ CONFIGURACIÓN Y EJECUCIÓN DEL BACKEND

Estos comandos te permiten configurar el entorno, instalar dependencias y ejecutar los tests del proyecto.

🧩 1. Crear el entorno virtual
python -m venv venv

▶️ 2. Activar el entorno virtual
venv\Scripts\activate

💡 Si aparece un error de permisos, ejecutá lo siguiente y volvé a intentar:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate

📦 3. Instalar las dependencias del proyecto
pip install -r requirements.txt

🧪 4. Ejecutar tests
Para correr un test específico:
pytest entradas/tests/test_comprar_entradas.py -v

Para mostrar solo los tests que pasaron:
pytest -v | findstr PASSED

🚪 5. Salir del entorno virtual
deactivate

📘 GUÍA PARA MANEJAR LA BASE DE DATOS DEL PROYECTO

El proyecto utiliza SQLite como base de datos local.
El archivo db.sqlite3 no se sube al repositorio, ya que está listado en .gitignore.
Cada integrante genera su propia base de datos a partir de las migraciones.

🧩 Cómo crear la base de datos local

python manage.py makemigrations
python manage.py migrate

Esto crea el archivo db.sqlite3 y todas las tablas necesarias en tu entorno local.

Si existe un archivo de datos iniciales (initial_data.json), podés cargarlo con:
python manage.py loaddata initial_data.json

🔁 Cómo mantener la base de datos actualizada

Cuando un integrante modifica los modelos del proyecto, debe crear y subir las migraciones al repositorio para que los demás puedan actualizar su base local.

Crear migraciones:
python manage.py makemigrations

Aplicarlas localmente:
python manage.py migrate

Subir los archivos de migración:
git add .
git commit -m "Agrega migraciones para los nuevos modelos"
git push

Los demás solo deben hacer:
git pull
python manage.py migrate

Esto actualizará su base local automáticamente al nuevo esquema.

💡 Consejo útil

Si tu base se desconfigura o querés regenerarla desde cero:
rm db.sqlite3
python manage.py migrate