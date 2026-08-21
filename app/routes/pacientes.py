from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Paciente, Consulta
from .auth import login_required

bp = Blueprint('pacientes', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    dni = request.args.get('dni')
    nombre = request.args.get('nombre')
    apellido = request.args.get('apellido')
    ordenar = request.args.get('ordenar', 'fecha_registro')

    query = Paciente.query
    if dni:
        query = query.filter(Paciente.dni.contains(dni))
    if nombre:
        query = query.filter(Paciente.nombre.contains(nombre))
    if apellido:
        query = query.filter(Paciente.apellido.contains(apellido))

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
@login_required
def nueva_paciente():
    if request.method == 'POST':
        try:
            dni = request.form.get('dni') or None
            if dni and Paciente.query.filter_by(dni=dni).first():
                flash(f'Error: El DNI {dni} ya está registrado.', 'error')
                paciente_temp = Paciente(**request.form)
                return render_template('nueva_paciente.html', paciente=None, form_data=paciente_temp)

            nuevo_paciente = Paciente(**request.form)
            if not dni:
                nuevo_paciente.dni = None
            db.session.add(nuevo_paciente)
            db.session.commit()
            flash('Paciente registrada exitosamente', 'success')
            return redirect(url_for('pacientes.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'error')
    return render_template('nueva_paciente.html', paciente=None)


@bp.route('/paciente/<int:id>')
@login_required
def ver_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(paciente_id=id).order_by(Consulta.id.desc()).all()
    return render_template('ver_paciente.html', paciente=paciente, consultas=consultas)


@bp.route('/paciente/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        dni = request.form.get('dni') or None
        existente = Paciente.query.filter(Paciente.dni == dni, Paciente.id != id).first()
        if dni and existente:
            flash(f'Error: El DNI {dni} ya pertenece a otra paciente.', 'error')
            return render_template('nueva_paciente.html', paciente=paciente)
        for key, value in request.form.items():
            if hasattr(paciente, key):
                setattr(paciente, key, (value or None) if key == 'dni' else value)
        db.session.commit()
        flash('Datos actualizados', 'success')
        return redirect(url_for('pacientes.ver_paciente', id=id))
    return render_template('nueva_paciente.html', paciente=paciente)


@bp.route('/paciente/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)
    db.session.commit()
    flash('Paciente eliminada', 'success')
    return redirect(url_for('pacientes.index'))


