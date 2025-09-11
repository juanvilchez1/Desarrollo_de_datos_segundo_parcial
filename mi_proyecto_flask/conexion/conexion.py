import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host='localhost',
        port=3307,  
        user='root',
        password='2006',
        database='desarrollo_web'
    )
    return conexion

