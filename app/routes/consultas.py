from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Consulta, Paciente
from .auth import login_required

bp = Blueprint('consultas', __name__)


@bp.route('/paciente/<int:id>/nueva_consulta', methods=['GET', 'POST'])
@login_required
def nueva_consulta(id):
    paciente = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        consulta = Consulta(paciente_id=id, **request.form)
        db.session.add(consulta)
        db.session.commit()
        flash('Consulta guardada', 'success')
        return redirect(url_for('pacientes.ver_paciente', id=id))
    return render_template('nueva_consulta.html', paciente=paciente)


@bp.route('/consulta/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    if request.method == 'POST':
        for key, value in request.form.items():
            if hasattr(consulta, key):
                setattr(consulta, key, value)
        db.session.commit()
        flash('Consulta actualizada correctamente', 'success')
        return redirect(url_for('pacientes.ver_paciente', id=consulta.paciente_id))
    paciente = Paciente.query.get(consulta.paciente_id)
    return render_template('nueva_consulta.html', paciente=paciente, consulta=consulta)


@bp.route('/consulta/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    paciente_id = consulta.paciente_id
    db.session.delete(consulta)
    db.session.commit()
    flash('Consulta eliminada', 'success')
    return redirect(url_for('pacientes.ver_paciente', id=paciente_id))


