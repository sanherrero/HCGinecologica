# Arquitectura del Sistema - Historia Clínica Ginecológica

Este proyecto utiliza el patrón **Application Factory** y la modularización mediante **Flask Blueprints**.

---

## Estructura de Directorios

```text
HCGinecologica/
│
├── app/
│   ├── __init__.py          # Application Factory (create_app) y registro de blueprints
│   ├── config.py            # Configuraciones del entorno (Config, DevConfig, ProdConfig)
│   ├── extensions.py        # Instancias de extensiones Flask (db, migrate)
│   ├── models.py            # Modelos SQLAlchemy (User, Paciente, Consulta, Archivo)
│   │
│   ├── routes/              # Módulos / Blueprints de la aplicación
│   │   ├── __init__.py
│   │   ├── auth.py          # Autenticación (login, logout, @login_required)
│   │   ├── pacientes.py     # Gestión de pacientes (listado, búsqueda, alta, vista, edición, baja)
│   │   ├── consultas.py     # Gestión de consultas clínicas (alta, edición, eliminación)
│   │   └── archivos.py      # Subida, visualización y eliminación de estudios / archivos
│   │
│   └── templates/           # Plantillas HTML con Jinja2 y Bootstrap 5
│       ├── layout.html
│       ├── login.html
│       ├── index.html
│       ├── nueva_paciente.html
│       ├── editar_paciente.html
│       ├── ver_paciente.html
│       └── nueva_consulta.html
│
├── uploads/                 # Directorio para almacenamiento de archivos y estudios adjuntos
├── pacientes.db             # Base de datos SQLite
├── wsgi.py                  # Entrypoint WSGI para servidores y desarrollo local
├── iniciar.bat              # Script batch para arranque en entorno Windows
├── requirements.txt         # Dependencias del proyecto
└── .env.example             # Ejemplo de variables de entorno
```

---

## Componentes Principales

### 1. Application Factory (`app/__init__.py`)
- Define la función `create_app(config_object=None)`.
- Configura las rutas para plantillas (`app/templates`) y subida de archivos (`uploads`).
- Inicializa extensiones (`SQLAlchemy`, `Flask-Migrate`).
- Registra los 4 Blueprints modulares:
  - `auth`
  - `pacientes`
  - `consultas`
  - `archivos`

### 2. Entrypoint WSGI (`wsgi.py`)
- Expone la variable `app = create_app()`.
- Proporciona la función `create_default_user()` para inicializar tablas y crear el usuario administrador por defecto (`admin`/`admin`) si no existe.
- Al ejecutarse como script principal (`python wsgi.py` o `iniciar.bat`), inicia el servidor de desarrollo en `http://127.0.0.1:5001` y abre automáticamente el navegador.
- Es compatible con servidores de producción (Gunicorn, Waitress, etc.).

### 3. Módulos y Blueprints
- **`auth`**: Provee el decorador `@login_required` para proteger todas las vistas y maneja el ciclo de vida de la sesión.
- **`pacientes`**: Permite buscar pacientes de forma parcial por DNI, Nombre o Apellido, ordenar por diferentes columnas, registrar nuevas pacientes, editar datos y eliminarlas.
- **`consultas`**: Administra el historial de consultas médicas vinculadas a cada paciente (antecedentes, examen físico, diagnóstico, tratamiento, observaciones).
- **`archivos`**: Administra los archivos y estudios clínicos asociados a cada paciente con nombres securizados.

---

## Ejecución

### En Windows (Desarrollo):
Hacer doble clic en `iniciar.bat` o ejecutar:
```cmd
python wsgi.py
```

### En Producción (Servidor WSGI):
```bash
gunicorn "wsgi:app" --bind 0.0.0.0:5001
```
