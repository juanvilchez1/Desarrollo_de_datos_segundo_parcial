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

# ---------------- RUTAS USUARIOS ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password_plano = request.form['password']
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', nombre=current_user.nombre)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

# ---------------- RUTAS CRUD PRODUCTOS ---------------- #

@app.route('/productos')
@login_required
def productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('productos.html', productos=productos)

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']

        if not nombre or not precio or not stock:
            return render_template('crear.html', mensaje="Todos los campos son obligatorios.")

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, precio, stock)
            VALUES (%s, %s, %s)
        """, (nombre, precio, stock))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('productos'))
    return render_template('crear.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        cursor.execute("""
            UPDATE productos
            SET nombre = %s, precio = %s, stock = %s
            WHERE id_producto = %s
        """, (nombre, precio, stock, id))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('productos'))

    cursor.execute("SELECT nombre, precio, stock FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar.html', producto=producto, id=id)

@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('productos'))
    return render_template('eliminar.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
    