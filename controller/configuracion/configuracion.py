from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox,
                             QDialog, QLineEdit, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from controller.recordatorio.recordatorio_core import Recordatorio
# from model.configuracion.servicios_usuario import UserService ## ELIMINADO: Reemplazaremos esta importación
from model.configuracion.mensajes import MessageHandler
from view.configuracion.formulario_usuario import UpdateUserForm
from view.configuracion.formulario_clave import PasswordForm
from view.configuracion.formulario_recordatorio import ReminderForm
from model.util.usuario_manager import BaseWidget
import os
import subprocess
import sys
import tempfile
import time
from model.util.colores import *
from model.util.mensajes import *

# MODIFICACIÓN: Se añaden las librerías para la comunicación con la API
import requests
import json

# MODIFICACIÓN: Se define la URL base donde corre tu API FastAPI
API_BASE_URL = "http://127.0.0.1:8000"

# --- NUEVA CLASE UserService PARA CONECTARSE A LA API ---
class UserService:
    """
    Servicio para interactuar con la API de usuarios.
    Maneja la obtención de datos del usuario autenticado.
    """
    def __init__(self, usuario, token):
        """
        Inicializa el servicio con el nombre de usuario y el token de autenticación.
        Args:
            usuario (str): El nombre del usuario.
            token (str): El token JWT para la autenticación.
        """
        self.usuario = usuario
        self.token = token
        # Preparamos el header de autorización que se usará en todas las peticiones
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def cargar_datos_usuario(self):
        """
        Obtiene los datos del usuario desde el endpoint /users/me/ de la API.
        Returns:
            tuple: Una tupla con los datos del usuario en el orden esperado por la UI:
                   (fecha_nacimiento, genero, peso, nivel_actividad, meta_cal, estatura).
        Raises:
            Exception: Si ocurre un error de conexión, autenticación o de servidor.
        """
        if not self.token:
            raise Exception("No se ha proporcionado un token de autenticación.")
            
        try:
            # Realizamos la petición GET al endpoint protegido
            response = requests.get(f"{API_BASE_URL}/users/me/", headers=self.headers)
            
            # Si la respuesta es un error (4xx o 5xx), lanzará una excepción
            response.raise_for_status() 
            
            # Convertimos la respuesta JSON en un diccionario de Python
            user_data = response.json()
            
            # Devolvemos los datos en el formato de tupla que la UI espera.
            # Nota: La API usa 'altura' y la UI espera 'estatura'. Hacemos el mapeo aquí.
            return (
            user_data.get('fecha_nacimiento'), # En lugar de 'edad'
            user_data.get('genero'),
            user_data.get('peso'),
            user_data.get('nivel_actividad'),
            user_data.get('meta_calorias'),
            user_data.get('altura') 
        )
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                raise Exception("Token inválido o expirado. Por favor, inicie sesión de nuevo.")
            else:
                raise Exception(f"Error HTTP: {http_err} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Error de conexión con el servidor: {req_err}")
        except Exception as e:
            raise Exception(f"Ocurrió un error inesperado al cargar los datos: {e}")

# --- Clases de la Interfaz (Widgets) ---

class InfoButton(QPushButton):
    """Botón de información personalizado"""
    def __init__(self, text="i", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(35, 35)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 18px;
                font-style: italic;
                font-family: 'Times New Roman';
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)

class ConfigFrame(QFrame):
    """Frame personalizado para la configuración"""
    def __init__(self, width, height, bg_color="#2C3E50", parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 15px;
                padding: 10px;
            }}
        """)

class ConfigLabel(QLabel):
    """Label personalizado para mostrar información del usuario"""
    def __init__(self, text, color="white", font_size=14, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                background-color: transparent;
                padding: 4px;
                font-family: Arial;
            }}
        """)

class ConfigButton(QPushButton):
    """Botón personalizado para configuración"""
    def __init__(self, text, width=420, height=65, bg_color="#2ECC71", 
                 hover_color="#27AE60", text_color="#2C3E50", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #7F8C8D;
                color: #BDC3C7;
            }}
        """)

class DangerButton(QPushButton):
    """Botón de peligro personalizado"""
    def __init__(self, text, width=200, height=40, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
            QPushButton:pressed {{
                background-color: #A93226;
            }}
        """)

class PasswordDialog(QDialog):
    """Diálogo para confirmar eliminación de cuenta"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Eliminación de Cuenta")
        self.setFixedSize(450, 280)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Título
        title_label = QLabel("Ingresa tu contraseña")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 22))
        title_label.setStyleSheet("color: #2C3E50; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Campo de contraseña
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setFixedSize(280, 45)
        self.password_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 22px;
                padding: 10px 15px;
                font-size: 16px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
        """)
        
        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_layout.addWidget(self.password_entry)
        password_layout.addStretch()
        layout.addLayout(password_layout)
        
        # Botones
        self.confirm_btn = QPushButton("Confirmar Eliminación")
        self.confirm_btn.setFixedSize(230, 45)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 22px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(230, 45)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 22px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Conectar señales
        self.cancel_btn.clicked.connect(self.reject)

class ConfigUI(QWidget, BaseWidget):
    datos_usuario_actualizados = pyqtSignal()

    # MODIFICACIÓN: El constructor ahora debe recibir el token de autenticación
    def __init__(self, panel_principal, color, usuario=None, token=None):
        QWidget.__init__(self, panel_principal)
        BaseWidget.__init__(self, parent=panel_principal, usuario=usuario)
        
        self.panel_principal = panel_principal
        self.color = color
        self.usuario = usuario if usuario else self.get_current_user()
        
        # MODIFICACIÓN: Se instancia el nuevo UserService con el usuario y el token
        self.user_service = UserService(self.usuario, token)
        
        self.recordatorio = Recordatorio(self.usuario)
        self.temp_dir = tempfile.mkdtemp()
        
        self.init_ui()
        self.setup_styles()
        
    def refrescar_vista(self):
        """
        Slot público que recarga la información del usuario en el panel.
        """
        print("RECIBIENDO SEÑAL: Refrescando vista de Configuración...")
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.load_user_data(self.info_layout)
        self.create_session_buttons(self.info_layout)

    def get_current_user(self):
        """Obtiene el usuario actual"""
        try:
            with open('usuario_actual.txt', 'r') as f:
                return f.read().strip()
        except:
            return "usuario_default"

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Configuración")
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: none;
            }
        """)
        main_layout.addWidget(self.main_frame)
        
        content_layout = QVBoxLayout(self.main_frame)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(20)
        
        self.create_header(content_layout)
        self.create_title_section(content_layout)
        self.create_main_content(content_layout)

    def create_header(self, parent_layout):
        """Crea el header con el botón de ayuda"""
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.boton_ayuda = InfoButton("i")
        self.boton_ayuda.clicked.connect(self.mostrar_advertencia)
        header_layout.addWidget(self.boton_ayuda)
        
        parent_layout.addLayout(header_layout)

    def create_title_section(self, parent_layout):
        """Crea la sección del título"""
        title_frame = QFrame()
        title_frame.setFixedHeight(80)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2ECC71;
                border-radius: 25px;
            }
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.titulo_label = QLabel("Configuración")
        self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 36px;
                font-weight: bold;
                font-family: Arial;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(self.titulo_label)
        
        parent_layout.addWidget(title_frame)

    def create_main_content(self, parent_layout):
        """Crea el contenido principal"""
        content_container = QHBoxLayout()
        content_container.setSpacing(30)
        content_container.setContentsMargins(0, 0, 0, 0)
        
        self.create_buttons_panel(content_container)
        self.create_user_info_panel(content_container)
        
        parent_layout.addLayout(content_container)
        parent_layout.addStretch()

    def create_buttons_panel(self, parent_layout):
        """Crea el panel de botones"""
        buttons_frame = QFrame()
        buttons_frame.setFixedWidth(480)
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(40)
        buttons_layout.setContentsMargins(30, 40, 30, 40)
        
        self.guardar_button = ConfigButton("Actualizar información")
        self.guardar_button.clicked.connect(self.mostrar_interfaz_guardar)
        buttons_layout.addWidget(self.guardar_button)
        
        self.mostrar_contra_button = ConfigButton("Actualizar Contraseña")
        self.mostrar_contra_button.clicked.connect(self.mostrar_formulario_contrasena)
        buttons_layout.addWidget(self.mostrar_contra_button)
        
        self.config_peso_button = ConfigButton("Configurar Recordatorio Peso")
        self.config_peso_button.clicked.connect(self.mostrar_formulario_recordatorio)
        buttons_layout.addWidget(self.config_peso_button)
        
        buttons_layout.addStretch()
        parent_layout.addWidget(buttons_frame)

    def create_user_info_panel(self, parent_layout):
        """Crea el panel de información del usuario"""
        outer_frame = QFrame()
        outer_frame.setFixedWidth(320)
        outer_frame.setStyleSheet("""
            QFrame {
                background-color: #95A5A6;
                border-radius: 20px;
                padding: 15px;
            }
        """)
        
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(15, 15, 15, 15)
        
        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        self.info_layout = QVBoxLayout(inner_frame)
        self.info_layout.setSpacing(12)
        self.info_layout.setContentsMargins(20, 20, 20, 20)
        
        self.load_user_data(self.info_layout)
        self.create_session_buttons(self.info_layout)
        
        outer_layout.addWidget(inner_frame)
        parent_layout.addWidget(outer_frame)

    def load_user_data(self, layout):
        """Carga y muestra los datos del usuario llamando a la API."""
        try:
            # Esta llamada ahora va a la API a través de nuestra nueva clase UserService
            fecha_nacimiento, genero, peso, nivel_actividad, meta_cal, estatura = self.user_service.cargar_datos_usuario()
            
            self.nombre_label = ConfigLabel(f"Nombre: {self.usuario}", font_size=15)
            self.edad_label = ConfigLabel(f"Edad: {fecha_nacimiento}")
            self.genero_label = ConfigLabel(f"Género: {genero}")
            self.peso_label = ConfigLabel(f"Peso: {peso} kg")
            self.estatura_label = ConfigLabel(f"Estatura: {estatura} cm")
            self.obj_calorias_label = ConfigLabel(f"Objetivo: {meta_cal} cal")
            self.lvl_actividad_label = ConfigLabel(f"Actividad: {nivel_actividad}")
            
            layout.addWidget(self.nombre_label)
            layout.addWidget(self.edad_label)
            layout.addWidget(self.genero_label)
            layout.addWidget(self.peso_label)
            layout.addWidget(self.estatura_label)
            layout.addWidget(self.obj_calorias_label)
            layout.addWidget(self.lvl_actividad_label)
            
        except Exception as e:
            # El manejo de errores ahora mostrará problemas de red, autenticación, etc.
            error_label = ConfigLabel(f"Error al cargar datos:\n{str(e)}", color="#E74C3C")
            layout.addWidget(error_label)

    def create_session_buttons(self, layout):
        """Crea los botones de sesión"""
        layout.addStretch()
        
        self.cerrar_sesion_button = DangerButton("Cerrar Sesión")
        self.cerrar_sesion_button.clicked.connect(self.cerrar_sesion)
        layout.addWidget(self.cerrar_sesion_button)
        
        self.borrar_cuenta_button = DangerButton("Borrar Cuenta")
        self.borrar_cuenta_button.clicked.connect(self.ventana_borrar_cuenta)
        layout.addWidget(self.borrar_cuenta_button)

    def setup_styles(self):
        """Configura los estilos generales"""
        self.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                font-family: Arial;
            }
        """)

    # El resto de los métodos de la clase (mostrar_mensaje, cerrar_sesion, etc.)
    # no necesitan cambios para esta integración y se dejan como estaban.
    # ... (resto de métodos sin cambios) ...
    def mostrar_mensaje_inicial(self):
        """Muestra mensaje inicial desde el archivo central"""
        info = MENSAJES.get("configuracion", {})
        titulo = info.get("titulo", "Configuración")
        mensaje = info.get("mensaje_html", "Bienvenido a la configuración.")
        
        QTimer.singleShot(1000, lambda: self.mostrar_mensaje(mensaje, titulo))
        
    def mostrar_mensaje(self, mensaje, titulo):
        """Muestra un mensaje informativo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)    
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def mostrar_advertencia(self):
        """Muestra la advertencia de información"""
        self.mostrar_mensaje(
            "Esta es la pestaña de configuracion, dentro podras configurar todo lo que es tu perfil como el objetivo de calorias y el nivel de actividad.",
            "Configuracion"
        )

    def mostrar_interfaz_guardar(self):
        """Muestra el diálogo para guardar datos."""
        dialog = UpdateUserForm(self.user_service, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevos_datos = dialog.get_data()
            try:
                exito_al_guardar = self.user_service.actualizar_datos(nuevos_datos)
                
                if exito_al_guardar:
                    QMessageBox.information(self, "Éxito", "La información ha sido actualizada.")
                    
                    self.refrescar_vista()
                    self.datos_usuario_actualizados.emit()
                else:
                    self.mostrar_error("Error de Guardado", "No se pudieron guardar los cambios en la base de datos.")
                
            except Exception as e:
                self.mostrar_error(f"Error al procesar los datos: {e}")
                
    def mostrar_formulario_contrasena(self):
        """Muestra el diálogo para cambiar la contraseña."""
        try:
            dialog = PasswordForm(self.user_service, self)
            dialog.exec()
        except Exception as e:
            self.mostrar_error(f"Error al abrir formulario de contraseña: {str(e)}")

    def mostrar_formulario_recordatorio(self):
        """Muestra el diálogo para configurar el recordatorio."""
        try:
            dialog = ReminderForm(self.user_service, self)
            dialog.exec()
        except Exception as e:
            self.mostrar_error(f"Error al abrir formulario de recordatorio: {str(e)}")
                                                
    def recreate_user_info(self):
        """Recrea la información del usuario"""
        pass

    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        reply = QMessageBox.question(
            self, 
            "Cerrar Sesión",
            "¿Estás seguro de que deseas cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mostrar_mensaje("Sesión cerrada.", "Cerrar sesión")
            QTimer.singleShot(2000, self.reiniciar_aplicacion)

    def ventana_borrar_cuenta(self):
        """Abre la ventana para borrar cuenta"""
        dialog = PasswordDialog(self)
        dialog.confirm_btn.clicked.connect(lambda: self.eliminar_cuenta(dialog))
        dialog.exec()

    def eliminar_cuenta(self, dialog):
        """Elimina la cuenta del usuario"""
        contra_ingresada = dialog.password_entry.text()
        
        if not contra_ingresada:
            self.mostrar_error("Por favor ingresa tu contraseña.")
            return
        
        try:
            exito = self.user_service.eliminar_usuario(contra_ingresada)
            
            if not exito:
                self.mostrar_error("La contraseña es incorrecta.")
                return
            
            reply = QMessageBox.question(
                self,
                "Última Confirmación",
                "¿REALMENTE estás seguro de eliminar tu cuenta? Todos tus datos se perderán.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                dialog.reject()
                return
            
            with open('usuario_actual.txt', 'w') as f:
                f.write('')
            
            self.mostrar_mensaje("Cuenta eliminada. La aplicación se cerrará.", "Éxito")
            dialog.accept()
            QTimer.singleShot(2000, self.reiniciar_aplicacion)
            
        except Exception as e:
            self.mostrar_error(f"Error al eliminar cuenta: {str(e)}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()

    def reiniciar_aplicacion(self):
        """Reinicia la aplicación"""
        try:
            QApplication.quit()
            time.sleep(1)
            python = sys.executable
            script_path = os.path.abspath("main.py")
            subprocess.Popen([python, script_path])
            sys.exit()
        except Exception as e:
            print(f"Error al reiniciar aplicación: {e}")
            sys.exit()

def mensage(self, mensaje, titulo):
    """Función de compatibilidad para mostrar mensajes"""
    self.mostrar_mensaje(mensaje, titulo)