from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import User

bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('pacientes.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado la sesión.', 'success')
    return redirect(url_for('auth.login'))
