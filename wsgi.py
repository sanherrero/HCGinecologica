import webbrowser
from threading import Timer
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()


def create_default_user():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            print("Creando usuario por defecto: admin")
            admin_user = User(username='admin')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()


if __name__ == '__main__':
    create_default_user()

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5001/login")

    Timer(1.5, open_browser).start()

    print("Iniciando servidor en http://127.0.0.1:5001 ...")
    app.run(debug=True, port=5001, use_reloader=False)


