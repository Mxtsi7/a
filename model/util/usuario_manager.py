# model/util/usuario_manager.py
import sqlite3
import os
import requests
import json
from PyQt6.QtWidgets import QMessageBox

class UsuarioManager:
    """Clase para manejar la gestión de usuarios, interactuando con una API y BD local."""
    
    @staticmethod
    def _get_api_url():
        """Devuelve la URL base de la API. Centralizado para fácil modificación."""
        return "http://127.0.0.1:8000"

    @staticmethod
    def _save_token(token):
        """Guarda el token de sesión JWT en un archivo local."""
        try:
            with open('session_token.txt', 'w') as f:
                f.write(token)
        except Exception as e:
            print(f"Error al guardar el token: {e}")

    @staticmethod
    def _get_token():
        """Recupera el token de sesión JWT desde el archivo local."""
        try:
            if not os.path.exists('session_token.txt'):
                return None
            with open('session_token.txt', 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error al leer el token: {e}")
            return None

    @staticmethod
    def login_user(username, password):
        """
        Autentica al usuario contra la API. Si es exitoso, guarda el token y el nombre de usuario.
        Retorna los datos del usuario en caso de éxito, de lo contrario None.
        """
        api_url = f"{UsuarioManager._get_api_url()}/login/"
        try:
            response = requests.post(
                api_url,
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                if token:
                    UsuarioManager._save_token(token)
                    UsuarioManager.establecer_usuario_actual(username)
                    print(f"Login exitoso para el usuario: {username}")
                    # Tras un login exitoso, obtenemos los datos del usuario
                    return UsuarioManager.get_user_data_from_api()
                else:
                    print("Error de login: El token no se encontró en la respuesta.")
                    return None
            else:
                print(f"Error de login. Status: {response.status_code}, Detalle: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API durante el login: {e}")
            return None

    @staticmethod
    def get_user_data_from_api():
        """
        Obtiene los datos del usuario actualmente autenticado desde el endpoint /users/me/ de la API.
        """
        token = UsuarioManager._get_token()
        if not token:
            print("No se pueden obtener los datos del usuario: No se encontró token de sesión.")
            return None

        api_url = f"{UsuarioManager._get_api_url()}/users/me/"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"Datos obtenidos exitosamente para el usuario: {user_data.get('nombre_usuario')}")
                return user_data
            elif response.status_code == 401:
                print("Error al obtener datos: Token inválido o expirado.")
                UsuarioManager.logout_user() # Limpiamos la sesión inválida
                return None
            else:
                print(f"Error al obtener datos. Status: {response.status_code}, Detalle: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API al obtener datos del usuario: {e}")
            return None

    @staticmethod
    def logout_user():
        """Cierra la sesión del usuario eliminando los archivos locales de sesión."""
        if os.path.exists('usuario_actual.txt'):
            os.remove('usuario_actual.txt')
        if os.path.exists('session_token.txt'):
            os.remove('session_token.txt')
        print("Sesión cerrada. Archivos de sesión eliminados.")

    @staticmethod
    def obtener_usuario_actual():
        """Obtiene el nombre de usuario actual desde el archivo local."""
        try:
            if os.path.exists('usuario_actual.txt'):
                with open('usuario_actual.txt', 'r') as file:
                    usuario = file.readline().strip()
                    return usuario if usuario else None
            return None
        except Exception as e:
            print(f"Error al obtener usuario actual: {e}")
            return None
    
    @staticmethod
    def establecer_usuario_actual(usuario):
        """Establece el usuario actual en el archivo local."""
        try:
            with open('usuario_actual.txt', 'w') as file:
                file.write(usuario)
            return True
        except Exception as e:
            print(f"Error al establecer usuario actual: {e}")
            return False
    
    @staticmethod
    def conectar_bd_usuario(usuario):
        """Conecta a la base de datos SQLite local específica del usuario."""
        try:
            db_path = f"./users/{usuario}/alimentos.db"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            UsuarioManager._crear_tablas_iniciales(conn, usuario)
            return conn
        except Exception as e:
            print(f"Error al conectar a BD del usuario {usuario}: {e}")
            return None
    
    @staticmethod
    def _crear_tablas_iniciales(conn, usuario):
        """Crea las tablas iniciales en la BD local de un nuevo usuario."""
        cursor = conn.cursor()
        try:
            cursor.execute('CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY, salud INTEGER DEFAULT 1, peso INTEGER DEFAULT 1, pulsaciones INTEGER DEFAULT 1, recordatorios INTEGER DEFAULT 1, agua INTEGER DEFAULT 1)')
            cursor.execute('CREATE TABLE IF NOT EXISTS peso (num INTEGER PRIMARY KEY AUTOINCREMENT, peso REAL NOT NULL, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
            cursor.execute('INSERT OR IGNORE INTO mensajes (id) VALUES (1)')
            conn.commit()
            print(f"Tablas locales iniciales creadas para el usuario: {usuario}")
        except Exception as e:
            print(f"Error al crear tablas iniciales: {e}")

    # --- El resto de las funciones (mostrar_mensaje_una_vez, resetear_mensajes) permanecen sin cambios ---
    @staticmethod
    def mostrar_mensaje_una_vez(parent, nombre_ventana, mensaje, titulo):
        usuario = UsuarioManager.obtener_usuario_actual()
        if not usuario: return
        conn = UsuarioManager.conectar_bd_usuario(usuario)
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(mensajes)")
            columnas = [col[1] for col in cursor.fetchall()]
            if nombre_ventana not in columnas:
                cursor.execute(f"ALTER TABLE mensajes ADD COLUMN {nombre_ventana} INTEGER DEFAULT 1")
                conn.commit()
            cursor.execute(f"SELECT {nombre_ventana} FROM mensajes WHERE id = 1")
            resultado = cursor.fetchone()
            if resultado and resultado[0] == 1:
                msg_box = QMessageBox(parent)
                msg_box.setWindowTitle(titulo)
                msg_box.setText(mensaje)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()
                cursor.execute(f"UPDATE mensajes SET {nombre_ventana} = 0 WHERE id = 1")
                conn.commit()
        except Exception as e:
            print(f"Error al manejar mensaje: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def resetear_mensajes(usuario=None):
        if not usuario: usuario = UsuarioManager.obtener_usuario_actual()
        if not usuario: return False
        conn = UsuarioManager.conectar_bd_usuario(usuario)
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE mensajes SET salud = 1, peso = 1, pulsaciones = 1, recordatorios = 1, agua = 1 WHERE id = 1")
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al resetear mensajes: {e}")
            return False
        finally:
            conn.close()

class BaseWidget:
    """Clase base para widgets que necesitan acceso a usuario y mensajes"""
    
    def __init__(self, parent=None, usuario=None):
        self.parent = parent
        self.usuario = usuario if usuario else UsuarioManager.obtener_usuario_actual()
        
        if not self.usuario:
            raise ValueError("No se ha proporcionado un usuario válido y no hay usuario actual configurado")
    
    def mostrar_mensaje_bienvenida(self, nombre_modulo, mensaje, titulo="Información"):
        """Muestra mensaje de bienvenida del módulo una sola vez"""
        UsuarioManager.mostrar_mensaje_una_vez(
            self.parent, 
            nombre_modulo, 
            mensaje, 
            titulo
        )
    
    def conectar_bd_usuario(self):
        """Conecta a la base de datos del usuario actual"""
        return UsuarioManager.conectar_bd_usuario(self.usuario)
    
    def mostrar_error(self, mensaje, titulo="Error"):
        """Muestra un mensaje de error"""
        if hasattr(self, 'parent') and self.parent:
            parent = self.parent
        else:
            parent = None
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
    
    def mostrar_info(self, mensaje, titulo="Información"):
        """Muestra un mensaje informativo"""
        if hasattr(self, 'parent') and self.parent:
            parent = self.parent
        else:
            parent = None
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()