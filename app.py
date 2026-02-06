from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import sys
import os
import webbrowser
from threading import Timer

# Inicialización

# Configuración para determinar rutas (necesario para el ejecutable)
if getattr(sys, 'frozen', False):
    # Si es un ejecutable (PyInstaller)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
    application_path = os.path.dirname(sys.executable)
else:
    # Si es desarrollo normal
    app = Flask(__name__)
    application_path = os.path.dirname(os.path.abspath(__file__))

# --- Configuración de Base de Datos ---
# Configura una base de datos SQLite temporal. 
db_path = os.path.join(application_path, 'pacientes.db')
upload_folder = os.path.join(application_path, 'uploads')
os.makedirs(upload_folder, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = 'clave_secreta_super_segura' # Necesario para mensajes flash

db = SQLAlchemy(app)

# Definición del Modelo

class Paciente(db.Model):
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
    
    # Antecedentes
    antecedentes_personales = db.Column(db.Text)
    medicacion_habitual = db.Column(db.Text)
    antecedentes_familiares = db.Column(db.Text)
    antecedentes_quirurgicos = db.Column(db.Text)
    alergias = db.Column(db.Text)
    habitos_tbq = db.Column(db.String(50))
    habitos_act_fisica = db.Column(db.String(100))
    
    # Ginecológicos / Obstétricos Base
    ginecologicos_rm = db.Column(db.String(50))
    ginecologicos_pareja = db.Column(db.String(100))
    ginecologicos_mac = db.Column(db.String(100))
    ginecologicos_cuello = db.Column(db.String(200)) # Historia de PAPs/Cuello
    obstetricos_gestas = db.Column(db.String(50))
    obstetricos_paridad = db.Column(db.String(50))
    obstetricos_pesos_fetales = db.Column(db.Text)
    obstetricos_patologias = db.Column(db.Text)
    
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    consultas = db.relationship('Consulta', backref='paciente', lazy=True, cascade="all, delete-orphan")
    archivos = db.relationship('Archivo', backref='paciente', lazy=True, cascade="all, delete-orphan")

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    fecha_consulta = db.Column(db.String(20))
    
    # Examen Físico
    peso = db.Column(db.String(20))
    tension_arterial = db.Column(db.String(20))
    ef_general = db.Column(db.Text)
    ef_mamas = db.Column(db.Text)
    ef_vulva = db.Column(db.Text)
    ef_cuello = db.Column(db.Text) # Examen actual
    
    # Ginecológico Actual
    fum = db.Column(db.String(20))
    mac = db.Column(db.String(100))
    
    # Control Obstétrico
    obs_au = db.Column(db.String(50)) # Altura Uterina
    obs_lcf = db.Column(db.String(50)) # Latidos
    obs_ecografia = db.Column(db.Text)
    obs_laboratorio = db.Column(db.Text)
    obs_solicito = db.Column(db.Text)
    obs_indico = db.Column(db.Text)
    
    motivo_consulta = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)

class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(200))
    fecha_subida = db.Column(db.DateTime, default=db.func.current_timestamp())


# Definición de las Rutas (Endpoints API)

@app.route('/', methods=['GET'])
def index():
    # Obtener parámetros de búsqueda y ordenamiento
    dni = request.args.get('dni')
    nombre = request.args.get('nombre')
    apellido = request.args.get('apellido')
    ordenar = request.args.get('ordenar', 'fecha_registro')

    # Construir la consulta
    query = Paciente.query

    if dni:
        query = query.filter(Paciente.dni == dni)
    if nombre:
        query = query.filter(Paciente.nombre == nombre)
    if apellido:
        query = query.filter(Paciente.apellido == apellido)

    # Ordenamiento
    if ordenar == 'nombre':
        query = query.order_by(Paciente.nombre)
    elif ordenar == 'apellido':
        query = query.order_by(Paciente.apellido)
    elif ordenar == 'dni':
        query = query.order_by(Paciente.dni)
    else:
        query = query.order_by(Paciente.fecha_registro.desc())

    pacientes = query.all()
    return render_template('index.html', pacientes=pacientes)

@app.route('/nueva_paciente', methods=['GET', 'POST'])
def nueva_paciente():
    if request.method == 'POST':
        try:
            dni = request.form.get('dni') or None
            # Validación: Verificar si el DNI ya existe
            if dni and Paciente.query.filter_by(dni=dni).first():
                flash(f'Error: El DNI {dni} ya está registrado.', 'error')
                # Retornamos los datos ingresados para no perderlos (usando un objeto temporal)
                paciente_temp = Paciente(nombre=request.form['nombre'], apellido=request.form['apellido'], dni=dni, fecha_nacimiento=request.form.get('fecha_nacimiento'), telefono=request.form.get('telefono'), direccion=request.form.get('direccion'))
                return render_template('nueva_paciente.html', paciente=None, form_data=paciente_temp)

            nuevo_paciente = Paciente(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=dni,
                fecha_nacimiento=request.form.get('fecha_nacimiento'),
                telefono=request.form.get('telefono'),
                direccion=request.form.get('direccion'),
                ocupacion=request.form.get('ocupacion'),
                obra_social=request.form.get('obra_social'),
                numero_afiliado=request.form.get('numero_afiliado'),
                antecedentes_personales=request.form.get('antecedentes_personales'),
                medicacion_habitual=request.form.get('medicacion_habitual'),
                antecedentes_familiares=request.form.get('antecedentes_familiares'),
                antecedentes_quirurgicos=request.form.get('antecedentes_quirurgicos'),
                alergias=request.form.get('alergias'),
                habitos_tbq=request.form.get('habitos_tbq'),
                habitos_act_fisica=request.form.get('habitos_act_fisica'),
                ginecologicos_rm=request.form.get('ginecologicos_rm'),
                ginecologicos_pareja=request.form.get('ginecologicos_pareja'),
                ginecologicos_mac=request.form.get('ginecologicos_mac'),
                ginecologicos_cuello=request.form.get('ginecologicos_cuello'),
                obstetricos_gestas=request.form.get('obstetricos_gestas'),
                obstetricos_paridad=request.form.get('obstetricos_paridad'),
                obstetricos_pesos_fetales=request.form.get('obstetricos_pesos_fetales'),
                obstetricos_patologias=request.form.get('obstetricos_patologias')
            )
            db.session.add(nuevo_paciente)
            db.session.commit()
            flash('Paciente registrada exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'error')
    return render_template('nueva_paciente.html', paciente=None)

@app.route('/paciente/<int:id>')
def ver_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(paciente_id=id).order_by(Consulta.id.desc()).all()
    return render_template('ver_paciente.html', paciente=paciente, consultas=consultas)

@app.route('/paciente/<int:id>/editar', methods=['GET', 'POST'])
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        dni = request.form.get('dni') or None
        # Validación: Verificar duplicados (excluyendo al paciente actual)
        existente = Paciente.query.filter_by(dni=dni).first()
        if dni and existente and existente.id != id:
            flash(f'Error: El DNI {dni} ya pertenece a otra paciente.', 'error')
            return render_template('nueva_paciente.html', paciente=paciente)

        paciente.nombre = request.form['nombre']
        paciente.apellido = request.form['apellido']
        paciente.dni = dni
        paciente.fecha_nacimiento = request.form.get('fecha_nacimiento')
        paciente.telefono = request.form.get('telefono')
        paciente.direccion = request.form.get('direccion')
        paciente.ocupacion = request.form.get('ocupacion')
        paciente.obra_social = request.form.get('obra_social')
        paciente.numero_afiliado = request.form.get('numero_afiliado')
        paciente.antecedentes_personales = request.form.get('antecedentes_personales')
        paciente.medicacion_habitual = request.form.get('medicacion_habitual')
        paciente.antecedentes_familiares = request.form.get('antecedentes_familiares')
        paciente.antecedentes_quirurgicos = request.form.get('antecedentes_quirurgicos')
        paciente.alergias = request.form.get('alergias')
        paciente.habitos_tbq = request.form.get('habitos_tbq')
        paciente.habitos_act_fisica = request.form.get('habitos_act_fisica')
        paciente.ginecologicos_rm = request.form.get('ginecologicos_rm')
        paciente.ginecologicos_pareja = request.form.get('ginecologicos_pareja')
        paciente.ginecologicos_mac = request.form.get('ginecologicos_mac')
        paciente.ginecologicos_cuello = request.form.get('ginecologicos_cuello')
        paciente.obstetricos_gestas = request.form.get('obstetricos_gestas')
        paciente.obstetricos_paridad = request.form.get('obstetricos_paridad')
        paciente.obstetricos_pesos_fetales = request.form.get('obstetricos_pesos_fetales')
        paciente.obstetricos_patologias = request.form.get('obstetricos_patologias')
        db.session.commit()
        flash('Datos actualizados', 'success')
        return redirect(url_for('ver_paciente', id=id))
    return render_template('nueva_paciente.html', paciente=paciente)

@app.route('/paciente/<int:id>/eliminar', methods=['POST'])
def eliminar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)
    db.session.commit()
    flash('Paciente eliminada', 'success')
    return redirect(url_for('index'))

@app.route('/paciente/<int:id>/nueva_consulta', methods=['GET', 'POST'])
def nueva_consulta(id):
    paciente = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        consulta = Consulta(
            paciente_id=id,
            fecha_consulta=request.form['fecha_consulta'],
            peso=request.form.get('peso'),
            tension_arterial=request.form.get('tension_arterial'),
            ef_general=request.form.get('ef_general'),
            ef_mamas=request.form.get('ef_mamas'),
            ef_vulva=request.form.get('ef_vulva'),
            ef_cuello=request.form.get('ef_cuello'),
            fum=request.form.get('fum'),
            mac=request.form.get('mac'),
            obs_au=request.form.get('obs_au'),
            obs_lcf=request.form.get('obs_lcf'),
            obs_ecografia=request.form.get('obs_ecografia'),
            obs_laboratorio=request.form.get('obs_laboratorio'),
            obs_solicito=request.form.get('obs_solicito'),
            obs_indico=request.form.get('obs_indico'),
            motivo_consulta=request.form.get('motivo_consulta'),
            diagnostico=request.form.get('diagnostico'),
            tratamiento=request.form.get('tratamiento'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(consulta)
        db.session.commit()
        flash('Consulta guardada', 'success')
        return redirect(url_for('ver_paciente', id=id))
    return render_template('nueva_consulta.html', paciente=paciente)

@app.route('/consulta/<int:id>/editar', methods=['GET', 'POST'])
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    paciente = Paciente.query.get(consulta.paciente_id)
    
    if request.method == 'POST':
        consulta.fecha_consulta = request.form['fecha_consulta']
        consulta.peso = request.form.get('peso')
        consulta.tension_arterial = request.form.get('tension_arterial')
        consulta.ef_general = request.form.get('ef_general')
        consulta.ef_mamas = request.form.get('ef_mamas')
        consulta.ef_vulva = request.form.get('ef_vulva')
        consulta.ef_cuello = request.form.get('ef_cuello')
        consulta.fum = request.form.get('fum')
        consulta.mac = request.form.get('mac')
        consulta.obs_au = request.form.get('obs_au')
        consulta.obs_lcf = request.form.get('obs_lcf')
        consulta.obs_ecografia = request.form.get('obs_ecografia')
        consulta.obs_laboratorio = request.form.get('obs_laboratorio')
        consulta.obs_solicito = request.form.get('obs_solicito')
        consulta.obs_indico = request.form.get('obs_indico')
        consulta.motivo_consulta = request.form.get('motivo_consulta')
        consulta.diagnostico = request.form.get('diagnostico')
        consulta.tratamiento = request.form.get('tratamiento')
        consulta.observaciones = request.form.get('observaciones')
        
        db.session.commit()
        flash('Consulta actualizada correctamente', 'success')
        return redirect(url_for('ver_paciente', id=paciente.id))
        
    return render_template('nueva_consulta.html', paciente=paciente, consulta=consulta)

@app.route('/consulta/<int:id>/eliminar', methods=['POST'])
def eliminar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    paciente_id = consulta.paciente_id
    db.session.delete(consulta)
    db.session.commit()
    flash('Consulta eliminada', 'success')
    return redirect(url_for('ver_paciente', id=paciente_id))

@app.route('/paciente/<int:id>/subir_archivo', methods=['POST'])
def subir_archivo(id):
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('ver_paciente', id=id))
    
    file = request.files['archivo']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('ver_paciente', id=id))
        
    if file:
        filename = secure_filename(f"{id}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        descripcion = request.form.get('descripcion')
        nuevo_archivo = Archivo(paciente_id=id, filename=filename, original_name=file.filename, descripcion=descripcion)
        db.session.add(nuevo_archivo)
        db.session.commit()
        flash('Archivo subido correctamente', 'success')
        
    return redirect(url_for('ver_paciente', id=id))

@app.route('/archivo/<int:id>/eliminar', methods=['POST'])
def eliminar_archivo(id):
    archivo = Archivo.query.get_or_404(id)
    paciente_id = archivo.paciente_id
    
    # Eliminar archivo físico si existe
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(archivo)
    db.session.commit()
    flash('Archivo eliminado correctamente', 'success')
    return redirect(url_for('ver_paciente', id=paciente_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Ejecución de la Aplicación

if __name__ == '__main__':
    # Crea la base de datos y la tabla Paciente si no existen
    with app.app_context():
        db.create_all()
    
    # Abrir el navegador automáticamente
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")
    
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()

    # Inicia el servidor Flask
    app.run(debug=True)