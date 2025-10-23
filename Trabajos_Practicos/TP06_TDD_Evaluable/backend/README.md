🚀 CÓMO EJECUTAR EN BACKEND PASO A PASO

Estos comandos te permiten configurar el entorno, instalar dependencias, crear el usuario por defecto y ejecutar los tests del proyecto.

🧹 Si ya existe una carpeta venv
Antes de crear un nuevo entorno virtual, eliminá el anterior (si ya existe):
Remove-Item -Recurse -Force .\venv

🧩 1. Crear el entorno virtual
python -m venv venv

▶️ 2. Activar el entorno virtual
venv\Scripts\activate

💡 Si aparece un error de permisos, ejecutá lo siguiente y volvé a intentar:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate

📦 3. Instalar dependencias
Primero instalá Django por las dudas:
pip install django
Luego instalá las dependencias del proyecto:
pip install -r requirements.txt

👤 4. Crear usuario por defecto (ID = 2)
Si todavía no existe la base de datos o necesitás un usuario predeterminado, ejecutá lo siguiente:
Entrar a la shell de Django:
python manage.py shell
Copiar y pegar el siguiente código dentro de la shell:
from django.contrib.auth.models import User

# Crear usuario con ID 2
user = User.objects.create_user(
    id=2,
    username='cliente_default',
    email='cliente@default.com',
    password='password123'
)
user.first_name = 'Cliente'
user.last_name = 'Default'
user.save()

print(f"Usuario creado: {user.username} (ID: {user.id})")

Salir de la shell con:
exit()

🧪 5. Ejecutar tests
Para correr un test específico:
pytest entradas/tests/test_comprar_entradas.py -v
Para mostrar solo los tests que pasaron:
pytest -v | findstr PASSED

🚪 6. Salir del entorno virtual
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