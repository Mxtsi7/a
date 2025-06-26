from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFrame, QMessageBox)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from model.login.auth_service import ApiService
from model.util.colores import *
from .form import *

class IniciarSesionForm(IForm, QWidget):

    volver_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: ApiService, on_success, on_back):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_back = on_back
        self.widgets = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border: 2px solid {azul_medio_oscuro};
                border-radius: 20px;
                padding: 15px;
                max-width: 240px;
            }}
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(6)

        titulo = QLabel("Iniciar Sesión")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro}; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)

        self.widgets['users_label'] = QLabel("Usuario")
        self.widgets['users_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial;
                border-radius: 15px;
                padding: 5px;
                min-width: 120px;
                min-height: 25px;
            }}
        """)
        self.widgets['users_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['users_label'])

        # --- CAMBIO: QComboBox reemplazado por QLineEdit ---
        self.widgets['user_entry'] = QLineEdit()
        self.widgets['user_entry'].setPlaceholderText("Ingrese su usuario")
        self.widgets['user_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry}; color: black; border-radius: 15px;
                padding: 6px 10px;
                min-width: 120px;
                min-height: 28px;
                font: 14px Arial;
            }}
        """)
        frame_layout.addWidget(self.widgets['user_entry'])

        self.widgets['contra_label'] = QLabel("Contraseña")
        self.widgets['contra_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial;
                border-radius: 15px;
                padding: 5px;
                min-width: 120px;
                min-height: 25px;
            }}
        """)
        self.widgets['contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['contra_label'])

        self.widgets['contra_entry'] = QLineEdit()
        self.widgets['contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry}; color: black; border-radius: 15px;
                padding: 6px 10px;
                min-width: 120px;
                min-height: 28px;
                font: 14px Arial;
            }}
        """)
        frame_layout.addWidget(self.widgets['contra_entry'])

        self.widgets['btn_iniciar_sesion'] = QPushButton("Iniciar Sesión")
        # Estilos de botones (sin cambios)
        btn_iniciar_palette = self.widgets['btn_iniciar_sesion'].palette()
        btn_iniciar_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_iniciar_sesion'].setPalette(btn_iniciar_palette)
        self.widgets['btn_iniciar_sesion'].setStyleSheet(f"""
            QPushButton {{
                background-color: {verde_boton}; border: none; border-radius: 18px;
                font: bold 14px Arial; padding: 8px; min-width: 140px; min-height: 30px;
            }}
            QPushButton:hover {{ background-color: {verde_oscuro}; }}
        """)
        frame_layout.addWidget(self.widgets['btn_iniciar_sesion'])
        
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        btn_volver_palette = self.widgets['btn_volver'].palette()
        btn_volver_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_volver'].setPalette(btn_volver_palette)
        self.widgets['btn_volver'].setStyleSheet(f"""
            QPushButton {{
                background-color: {riesgo_medio}; border: none; border-radius: 18px;
                font: bold 14px Arial; padding: 8px; min-width: 140px; min-height: 30px;
            }}
            QPushButton:hover {{ background-color: {riesgo_alto}; }}
        """)
        frame_layout.addWidget(self.widgets['btn_volver'])
        
        self.widgets['user_entry'].returnPressed.connect(self.widgets['contra_entry'].setFocus)
        self.widgets['contra_entry'].returnPressed.connect(self._iniciar_sesion)
        self.widgets['btn_iniciar_sesion'].clicked.connect(self._iniciar_sesion)
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        
        main_layout.addWidget(self.frame)

    def mostrar(self):
        self.widgets['user_entry'].clear()
        self.widgets['contra_entry'].clear()
        self.show()

    def ocultar(self):
        self.hide()
        
    def _volver_atras(self):
        self.volver_clicked.emit()

    def _iniciar_sesion(self):
        usuario = self.widgets['user_entry'].text()
        if not usuario:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa tu nombre de usuario.")
            return
            
        contrasena = self.widgets['contra_entry'].text()
        if not contrasena:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa tu contraseña.")
            return
        
        try:
            success, message = self.auth_service.login(usuario, contrasena)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.ocultar()
                self.on_success()
            else:
                QMessageBox.warning(self, "Error de Inicio de Sesión", message)
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Error al iniciar sesión: {str(e)}")