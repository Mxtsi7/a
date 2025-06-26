import os 
from datetime import timedelta

class ApiConfig:
    # Variables de entorno para APIs externas
    KeyCal = os.environ.get('KeyCal') or ''
    URL = os.environ.get('URL') or ''
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Configuraciones adicionales
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False