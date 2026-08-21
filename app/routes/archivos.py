import os
from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Archivo
from .auth import login_required

bp = Blueprint('archivos', __name__)


@bp.route('/paciente/<int:id>/subir_archivo', methods=['POST'])
@login_required
def subir_archivo(id):
    if 'archivo' not in request.files or request.files['archivo'].filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('pacientes.ver_paciente', id=id))
    file = request.files['archivo']
    if file:
        filename = secure_filename(f"{id}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        descripcion = request.form.get('descripcion')
        nuevo_archivo = Archivo(paciente_id=id, filename=filename, original_name=file.filename, descripcion=descripcion)
        db.session.add(nuevo_archivo)
        db.session.commit()
        flash('Archivo subido correctamente', 'success')
    return redirect(url_for('pacientes.ver_paciente', id=id))


@bp.route('/archivo/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_archivo(id):
    archivo = Archivo.query.get_or_404(id)
    paciente_id = archivo.paciente_id
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
    db.session.delete(archivo)
    db.session.commit()
    flash('Archivo eliminado correctamente', 'success')
    return redirect(url_for('pacientes.ver_paciente', id=paciente_id))


@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

