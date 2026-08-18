from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Consulta, Paciente

bp = Blueprint('consultas', __name__)

@bp.route('/paciente/<int:id>/nueva_consulta', methods=['GET', 'POST'])
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
        return redirect(url_for('pacientes.ver_paciente', id=id))
    return render_template('nueva_consulta.html', paciente=paciente)

@bp.route('/consulta/<int:id>/editar', methods=['GET', 'POST'])
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    paciente = Paciente.query.get(consulta.paciente_id)
    if request.method == 'POST':
        consulta.fecha_consulta = request.form['fecha_consulta']
        # ... actualizar campos como en el original
        db.session.commit()
        flash('Consulta actualizada correctamente', 'success')
        return redirect(url_for('pacientes.ver_paciente', id=paciente.id))
    return render_template('nueva_consulta.html', paciente=paciente, consulta=consulta)
