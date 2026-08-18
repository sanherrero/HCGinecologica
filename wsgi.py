from app import create_app

app = create_app()

# Entrypoint WSGI para Gunicorn u otros servidores
# Ejemplo de ejecución: gunicorn "wsgi:app"
