# 🚀 CONFIGURACIÓN Y EJECUCIÓN DEL BACKEND ------------------------------------------------------------

Este documento describe los pasos para configurar el entorno de desarrollo del backend, manejar la base de datos, ejecutar la aplicación y correr los tests.

## 📋 Prerrequisitos

* **Python:** Asegúrate de tener Python instalado (verifica la versión requerida por el proyecto).
* **pip:** El instalador de paquetes de Python (usualmente viene con Python).
* **Git:** Para clonar el repositorio.

## ⚙️ CONFIGURACIÓN INICIAL PASO A PASO

Sigue estos pasos para poner en marcha el proyecto en tu máquina local:

### 1. Crear y Activar el Entorno Virtual (venv)

# Elimina la carpeta venv anterior si existe (Comando para PowerShell)
Remove-Item -Recurse -Force .\venv
# Comando para Bash/Cmd (verifica antes de ejecutar!)
rm -rf venv || rmdir /s /q venv

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows (PowerShell/Cmd):
.\venv\Scripts\activate
# En Linux/macOS (Bash/Zsh):
source venv/bin/activate

# Nota para PowerShell en Windows: Si al activar obtienes un error de permisos, ejecuta
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 

# 2. Instalar Dependencias

pip install -r requirements.txt

# 3. Configurar la Base de Datos Local (SQLite)

# Crea las migraciones (si hay cambios en los modelos no migrados)
python manage.py makemigrations

# Aplica las migraciones para crear las tablas en db.sqlite3
python manage.py migrate

# (Opcional: Si existe un archivo initial_data.json con datos iniciales)
python manage.py loaddata initial_data.json

# 4. Crear Usuario por Defecto (Opcional, ID=2)

# Entra a la shell interactiva de Django
python manage.py shell

# Una vez dentro de la shell, ejecuta el siguiente código Python:
from django.contrib.auth.models import User
from django.db import IntegrityError

try:
    # Intentar crear usuario con ID 2
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
except IntegrityError:
    print("El usuario con ID 2 ya existe o el ID está en uso.")
except Exception as e:
    print(f"Ocurrió un error: {e}")

# Salir de la shell
exit()

# 6. Ejecutar el Servidor de Desarrollo
python manage.py runserver

# 🚪 Salir del Entorno Virtual
deactivate

# 🧪 EJECUTAR TESTS --------------------------------------------------------------------------------------

# Correr todos los tests verbosamente
pytest -v

# Correr un test específico verbosamente
pytest entradas/tests/test_comprar_entradas.py -v

# Filtrar tests por nombre (ejemplo: tests que contengan 'comprar')
pytest -k comprar -v

# Mostrar solo los tests que pasaron (usando filtro de pytest)
# (La opción 'findstr' es específica de Windows Cmd)
pytest -v -rP # -rP muestra resumen de PASSED

# 💾 GUÍA PARA MANEJAR LA BASE DE DATOS ------------------------------------------------------------------

# Creación Inicial
Ya cubierta en el paso 4 de la configuración (makemigrations, migrate).

# 💡 Mantener la Base de Datos Actualizada

# Cuando un desarrollador modifica los modelos (models.py):
python manage.py makemigrations
python manage.py migrate
git add .
git commit -m "Agrega migraciones para [breve descripción del cambio]"
git push

# Cuando otro desarrollador obtiene estos cambios:
git pull
python manage.py migrate

# 💡 Regenerar la Base de Datos desde Cero

Asegúrate de que tu entorno virtual esté activo.
Elimina el archivo db.sqlite3.

# En Windows (PowerShell)
Remove-Item db.sqlite3
# En Linux/macOS/Git Bash
rm db.sqlite3

# Aplica todas las migraciones existentes:
python manage.py migrate
python manage.py loaddata initial_data.json

# (Opcional) Vuelve a crear el usuario por defecto si lo necesitas (ver paso 5 de configuració