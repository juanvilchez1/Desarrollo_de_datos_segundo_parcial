from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from conexion.conexion import obtener_conexion
from models import Usuario

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Cargar usuario desde MySQL
@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, correo, password FROM usuarios WHERE id = %s", (user_id,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resultado:
        return Usuario(*resultado)
    return None

# ---------------- RUTAS ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

# Registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password_plano = request.form['password']

        # Encriptar contraseña
        password_hash = generate_password_hash(password_plano)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, password)
                VALUES (%s, %s, %s)
            """, (nombre, correo, password_hash))
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error en registro: {e}")
            return render_template('registro.html', mensaje="Error: el correo ya está registrado o hubo un problema.")
    return render_template('registro.html')

# Login de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, correo, password FROM usuarios WHERE correo = %s", (correo,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado and check_password_hash(resultado[3], password):
            usuario = Usuario(*resultado)
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', mensaje="Correo o contraseña incorrectos.")
    return render_template('login.html')

# Dashboard protegido
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', nombre=current_user.nombre)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Página "Acerca de"
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)