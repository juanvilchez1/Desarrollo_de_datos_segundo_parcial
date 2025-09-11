from flask import Flask, render_template, request, redirect, url_for
import json, csv, os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from conexion.conexion import obtener_conexion # ← nueva importación

app = Flask(__name__)

# SQLite setup
Base = declarative_base()
engine = create_engine('sqlite:///database/usuarios.db')
Session = sessionmaker(bind=engine)
session = Session()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    correo = Column(String)

Base.metadata.create_all(engine)

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    nombre = request.form['nombre']
    correo = request.form['correo']

    # Guardar en TXT
    with open('datos/datos.txt', 'a') as f:
        f.write(f'{nombre},{correo}\n')

    # Guardar en JSON
    datos_json = {'nombre': nombre, 'correo': correo}
    try:
        with open('datos/datos.json', 'r') as f:
            datos_existentes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        datos_existentes = []
    datos_existentes.append(datos_json)
    with open('datos/datos.json', 'w') as f:
        json.dump(datos_existentes, f, indent=4)

    # Guardar en CSV
    with open('datos/datos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([nombre, correo])

    # Guardar en SQLite
    nuevo_usuario = Usuario(nombre=nombre, correo=correo)
    session.add(nuevo_usuario)
    session.commit()

    # Guardar en MySQL
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)", (nombre, correo))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error al guardar en MySQL: {e}")
    return render_template('resultado.html', nombre=nombre, correo=correo)

@app.route('/ver_csv')
def ver_csv():
    with open('datos/datos.csv') as f:
        reader = csv.reader(f)
        datos = [{'nombre': row[0], 'correo': row[1]} for row in reader]
    return {'usuarios': datos}

@app.route('/ver_sqlite')
def ver_sqlite():
    usuarios = session.query(Usuario).all()
    datos = [{'nombre': u.nombre, 'correo': u.correo} for u in usuarios]
    return {'usuarios': datos}

@app.route('/ver_mysql')
def ver_mysql():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, correo FROM usuarios")
        resultados = cursor.fetchall()
        datos = [{'nombre': nombre, 'correo': correo} for nombre, correo in resultados]
        cursor.close()
        conexion.close()
        return {'usuarios': datos}
    except Exception as e:
        return {'error': str(e)}

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)