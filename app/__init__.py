import os
from flask import Flask
from .config import Config
from .extensions import db, migrate


def create_app(config_object=None):
    """Application factory."""
    # Apunta a la carpeta templates en la raíz del proyecto para mantener compatibilidad
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folder = os.path.join(project_root, 'templates')

    app = Flask(__name__, template_folder=template_folder)

    # Cargar configuración
    if config_object is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Crear carpeta de uploads si no existe
    upload_folder = app.config.get("UPLOAD_FOLDER", os.path.join(project_root, 'uploads'))
    os.makedirs(upload_folder, exist_ok=True)

    # Registrar blueprints
    from .routes.pacientes import bp as pacientes_bp
    from .routes.consultas import bp as consultas_bp
    from .routes.archivos import bp as archivos_bp

    app.register_blueprint(pacientes_bp)
    app.register_blueprint(consultas_bp)
    app.register_blueprint(archivos_bp)

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}

    return app
