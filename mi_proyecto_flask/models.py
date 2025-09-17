from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, nombre, correo, password):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password = password
        
        