from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Paciente(db.Model):
    __tablename__ = 'paciente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(15), unique=True, nullable=True)
    fecha_nacimiento = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    ocupacion = db.Column(db.String(100))
    obra_social = db.Column(db.String(100))
    numero_afiliado = db.Column(db.String(50))

    antecedentes_personales = db.Column(db.Text)
    medicacion_habitual = db.Column(db.Text)
    antecedentes_familiares = db.Column(db.Text)
    antecedentes_quirurgicos = db.Column(db.Text)
    alergias = db.Column(db.Text)
    habitos_tbq = db.Column(db.String(50))
    habitos_act_fisica = db.Column(db.String(100))

    ginecologicos_rm = db.Column(db.String(50))
    ginecologicos_pareja = db.Column(db.String(100))
    ginecologicos_mac = db.Column(db.String(100))
    ginecologicos_cuello = db.Column(db.String(200))
    obstetricos_gestas = db.Column(db.String(50))
    obstetricos_paridad = db.Column(db.String(50))
    obstetricos_pesos_fetales = db.Column(db.Text)
    obstetricos_patologias = db.Column(db.Text)

    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    consultas = db.relationship('Consulta', backref='paciente', lazy=True, cascade="all, delete-orphan")
    archivos = db.relationship('Archivo', backref='paciente', lazy=True, cascade="all, delete-orphan")


class Consulta(db.Model):
    __tablename__ = 'consulta'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    fecha_consulta = db.Column(db.String(20))
    peso = db.Column(db.String(20))
    tension_arterial = db.Column(db.String(20))
    ef_general = db.Column(db.Text)
    ef_mamas = db.Column(db.Text)
    ef_vulva = db.Column(db.Text)
    ef_cuello = db.Column(db.Text)
    fum = db.Column(db.String(20))
    mac = db.Column(db.String(100))
    obs_au = db.Column(db.String(50))
    obs_lcf = db.Column(db.String(50))
    obs_ecografia = db.Column(db.Text)
    obs_laboratorio = db.Column(db.Text)
    obs_solicito = db.Column(db.Text)
    obs_indico = db.Column(db.Text)
    motivo_consulta = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)


class Archivo(db.Model):
    __tablename__ = 'archivo'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(200))
    fecha_subida = db.Column(db.DateTime, default=db.func.current_timestamp())
