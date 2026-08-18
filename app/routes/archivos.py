from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os
from ..extensions import db
from ..models import Archivo

bp = Blueprint('archivos', __name__)

@bp.route('/paciente/<int:id>/subir_archivo', methods=['POST'])
def subir_archivo(id):
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('pacientes.ver_paciente', id=id))
    file = request.files['archivo']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('pacientes.ver_paciente', id=id))
    filename = secure_filename(f"{id}_{file.filename}")
    destino = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(destino)
    descripcion = request.form.get('descripcion')
    nuevo_archivo = Archivo(paciente_id=id, filename=filename, original_name=file.filename, descripcion=descripcion)
    db.session.add(nuevo_archivo)
    db.session.commit()
    flash('Archivo subido correctamente', 'success')
    return redirect(url_for('pacientes.ver_paciente', id=id))

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
