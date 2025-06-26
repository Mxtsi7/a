from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from marshmallow import Schema, fields, validate, ValidationError, validates
from Models import db, Usuario

class UsuarioRegistroSchema(Schema):
    nombre_usuario = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    genero = fields.Str(required=True, validate=validate.OneOf(['Masculino', 'Femenino']))
    peso = fields.Float(required=True, validate=validate.Range(min=30, max=300))
    altura = fields.Int(required=True, validate=validate.Range(min=100, max=250))
    meta_calorias = fields.Int(required=True, validate=validate.Range(min=1000, max=5000))
    nivel_actividad = fields.Str(required=True, validate=validate.OneOf(['Sedentario', 'Ligero', 'Moderado', 'Intenso']))
    fecha_nacimiento = fields.Date(required=True)
    
    @validates('fecha_nacimiento')  # ✅ Decorador correcto para validación automática
    def validate_fecha_nacimiento(self, value):
        """Valida que la edad esté entre 13 y 120 años"""
        today = date.today()
        edad = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if edad < 13 or edad > 120:
            raise ValidationError(f'La edad debe estar entre 13 y 120 años. Edad calculada: {edad} años')

class UsuarioLoginSchema(Schema):
    nombre_usuario = fields.Str(required=True)
    password = fields.Str(required=True)