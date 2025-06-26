# En: view/configuracion/formulario_clave.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from model.configuracion.servicios_usuario import UserService
# Nota: Ya no necesitamos importar FormHandler

class PasswordForm(QDialog):
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent) # Llamada al constructor de QDialog
        self.user_service = user_service
        self.widgets = {}

        # --- Configuración de la Ventana/Diálogo ---
        self.setWindowTitle("Actualizar Contraseña")
        self.setFixedSize(400, 420)
        self.setModal(True) # Importante: bloquea la ventana principal
        
        self.setStyleSheet("""
            QDialog { background-color: #2C3E50; color: white; font-family: Arial; }
            QLabel {
                background-color: transparent;
                color: white;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #f0f0f0; color: black; border: none;
                border-radius: 10px; padding: 8px; font-size: 12px;
            }
            QPushButton {
                background-color: #2ECC71; color: #2C3E50; border: none;
                border-radius: 15px; padding: 12px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #27AE60; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # --- Creación de Widgets ---
        self.widgets['nombre_label'] = QLabel(f"Usuario: {self.user_service.usuario}")
        layout.addWidget(self.widgets['nombre_label'])
        
        # Contraseña anterior
        self.widgets['contra_anterior_label'] = QLabel("Contraseña Actual")
        self.widgets['contra_anterior_entry'] = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        layout.addWidget(self.widgets['contra_anterior_label'])
        layout.addWidget(self.widgets['contra_anterior_entry'])
        
        # Nueva contraseña
        self.widgets['nueva_contra_label'] = QLabel("Nueva Contraseña")
        self.widgets['nueva_contra_entry'] = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        layout.addWidget(self.widgets['nueva_contra_label'])
        layout.addWidget(self.widgets['nueva_contra_entry'])
        
        # Confirmar contraseña
        self.widgets['confirmar_contra_label'] = QLabel("Confirmar Nueva Contraseña")
        self.widgets['confirmar_contra_entry'] = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        layout.addWidget(self.widgets['confirmar_contra_label'])
        layout.addWidget(self.widgets['confirmar_contra_entry'])
        
        layout.addStretch() # Espaciador
        
        # Botón actualizar
        self.widgets['actualizar_contra_button'] = QPushButton("Actualizar Contraseña")
        self.widgets['actualizar_contra_button'].clicked.connect(self.save)
        layout.addWidget(self.widgets['actualizar_contra_button'])

    def save(self):
        contra_anterior = self.widgets['contra_anterior_entry'].text()
        nueva_contra = self.widgets['nueva_contra_entry'].text()
        confirmar_contra = self.widgets['confirmar_contra_entry'].text()

        if not contra_anterior or not nueva_contra or not confirmar_contra:
            QMessageBox.warning(self, "Advertencia", "Completa todos los campos.")
            return

        if nueva_contra != confirmar_contra:
            QMessageBox.warning(self, "Advertencia", "Las nuevas contraseñas no coinciden.")
            return

        if self.user_service.actualizar_contrasena(contra_anterior, nueva_contra):
            QMessageBox.information(self, "Confirmación", "Contraseña actualizada correctamente.")
            self.accept()  # Cierra el diálogo con estado "Aceptado"
        else:
            QMessageBox.warning(self, "Error", "La contraseña actual es incorrecta.")