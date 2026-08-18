from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Aquí se pueden añadir otras extensiones (login, cors, etc.)
