from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Corregido: era __table__
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(30), unique=True, nullable=False)  # Unificado nombre
    password_hash = db.Column(db.String(128), nullable=False)  # Corregido: campo para hash
    genero = db.Column(db.String(10), nullable=False)
    peso = db.Column(db.Float, nullable=False)  # Corregido: sin especificar tamaño
    altura = db.Column(db.Integer, nullable=False)  # Cambiado a Integer para cm
    meta_calorias = db.Column(db.Integer, nullable=False)  # Unificado nombre
    nivel_actividad = db.Column(db.String(15), nullable=False)  # Unificado nombre
    fecha_nacimiento = db.Column(db.Date, nullable=False)  # Unificado nombre
    registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Establece la contraseña encriptada"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
        
    def calcular_edad(self):
        """Calcula la edad actual del usuario"""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id, 
            'nombre_usuario': self.nombre_usuario,  # Corregido nombre
            'genero': self.genero,
            'peso': self.peso,
            'altura': self.altura,
            'meta_calorias': self.meta_calorias,  # Corregido nombre
            'nivel_actividad': self.nivel_actividad,  # Corregido nombre
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'edad': self.calcular_edad(),  # Corregido: agregado ()
            'registro': self.registro.isoformat() if self.registro else None
        }