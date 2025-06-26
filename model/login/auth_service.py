import requests
import json

class ApiService:
    """
    Gestiona toda la comunicación con la API de FastAPI.
    Almacena el estado de la sesión (token y usuario actual).
    """
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.current_user = None

    def register(self, user_data: dict):
        """
        Envía una solicitud de registro a la API.
        Args:
            user_data (dict): Diccionario con los datos del nuevo usuario.
        Returns:
            tuple[bool, str]: (Éxito, Mensaje/Error)
        """
        try:
            response = requests.post(f"{self.base_url}/register/", json=user_data)
            
            if response.status_code == 201:
                return True, "Usuario registrado con éxito."
            
            # Intenta obtener el detalle del error desde el JSON de respuesta
            try:
                error_detail = response.json().get('detail', 'Error desconocido.')
                return False, f"Error ({response.status_code}): {error_detail}"
            except json.JSONDecodeError:
                return False, f"Error en el servidor ({response.status_code}): {response.text}"

        except requests.exceptions.RequestException as e:
            return False, f"Error de conexión: No se pudo conectar a la API. {e}"

    def login(self, username: str, password: str):
        """
        Envía una solicitud de login a la API para obtener un token.
        Si tiene éxito, guarda el token y el nombre de usuario.
        Args:
            username (str): Nombre de usuario.
            password (str): Contraseña.
        Returns:
            tuple[bool, str]: (Éxito, Mensaje/Error)
        """
        try:
            # FastAPI con OAuth2PasswordRequestForm espera los datos en 'form-data'
            login_data = {'username': username, 'password': password}
            response = requests.post(f"{self.base_url}/login/", data=login_data)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                # Almacenamos el nombre de usuario tras un login exitoso
                self.current_user = username 
                return True, "Inicio de sesión exitoso."
                
            try:
                error_detail = response.json().get('detail', 'Error desconocido.')
                return False, f"Error ({response.status_code}): {error_detail}"
            except json.JSONDecodeError:
                 return False, f"Error en el servidor ({response.status_code}): {response.text}"

        except requests.exceptions.RequestException as e:
            self.logout() # Limpia cualquier estado previo si falla la conexión
            return False, f"Error de conexión: No se pudo conectar a la API. {e}"

    def logout(self):
        """Limpia el estado de la sesión del usuario."""
        self.token = None
        self.current_user = None
        print("Sesión local cerrada.")

    def obtener_usuario_actual(self):
        """
        Devuelve el nombre del usuario que ha iniciado sesión.
        Este es el método que faltaba.
        """
        return self.current_user

    def get_auth_headers(self):
        """
        Construye el encabezado de autorización para las solicitudes protegidas.
        """
        if not self.token:
            return None
        return {"Authorization": f"Bearer {self.token}"}