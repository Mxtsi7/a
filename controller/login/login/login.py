from view.login.login_form import LoginForm
from model.login.user_database import UserDatabase
from model.login.auth_service import AuthService

class Log_in:
    def __init__(self, parent, on_success):
        # Inicializar servicios
        self.auth_service = AuthService()
        self.user_database = UserDatabase()
        
        # Limpiar usuario al iniciar
        self.auth_service.limpiar_usuario_actual()
        
        # Mostrar la interfaz de login, pasando el parent (Main) y la función de callback
        self.login_form = LoginForm(parent, self.auth_service, on_success)
        self.login_form.mostrar()