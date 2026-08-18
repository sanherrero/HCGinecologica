from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Paciente, Consulta, Archivo

bp = Blueprint('pacientes', __name__)

@bp.route('/', methods=['GET'])
def index():
    dni = request.args.get('dni')
    nombre = request.args.get('nombre')
    apellido = request.args.get('apellido')
    ordenar = request.args.get('ordenar', 'fecha_registro')

    query = Paciente.query
    if dni:
        query = query.filter(Paciente.dni == dni)
    if nombre:
        query = query.filter(Paciente.nombre == nombre)
    if apellido:
        query = query.filter(Paciente.apellido == apellido)

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

@bp.route('/nueva_paciente', methods=['GET', 'POST'])
def nueva_paciente():
    if request.method == 'POST':
        try:
            dni = request.form.get('dni') or None
            if dni and Paciente.query.filter_by(dni=dni).first():
                flash(f'Error: El DNI {dni} ya está registrado.', 'error')
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
            return redirect(url_for('pacientes.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'error')
    return render_template('nueva_paciente.html', paciente=None)

@bp.route('/paciente/<int:id>')
def ver_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(paciente_id=id).order_by(Consulta.id.desc()).all()
    return render_template('ver_paciente.html', paciente=paciente, consultas=consultas)
