# En: view/configuracion/formulario_recordatorio.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                             QCheckBox, QPushButton, QMessageBox)
from model.configuracion.servicios_usuario import UserService
# Nota: Ya no necesitamos importar FormHandler

class ReminderForm(QDialog):
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.widgets = {}
        
        # --- Configuración de la Ventana/Diálogo ---
        self.setWindowTitle("Configurar Recordatorio de Peso")
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog { background-color: #2C3E50; color: white; font-family: Arial; }
            QLabel {
                background-color: transparent; color: white; padding: 8px;
                font-size: 14px; font-weight: bold;
            }
            QComboBox {
                background-color: #cccccc; color: black; border: none;
                border-radius: 10px; padding: 8px; font-size: 12px;
            }
            QCheckBox { color: white; font-size: 14px; spacing: 10px; }
            QCheckBox::indicator { width: 20px; height: 20px; }
            QPushButton {
                background-color: #2ECC71; color: #2C3E50; border: none;
                border-radius: 15px; padding: 12px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #27AE60; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # --- Creación de Widgets ---
        self.widgets['label_recordatorio'] = QLabel("Frecuencia de Recordatorio")
        layout.addWidget(self.widgets['label_recordatorio'])
        
        self.widgets['tiempo_recordatorio_combobox'] = QComboBox()
        self.widgets['tiempo_recordatorio_combobox'].addItems(["1 día", "3 días", "5 días", "1 semana", "1 mes"])
        layout.addWidget(self.widgets['tiempo_recordatorio_combobox'])
        
        self.widgets['activar_recordatorio_checkbox'] = QCheckBox("Activar Recordatorio")
        layout.addWidget(self.widgets['activar_recordatorio_checkbox'])
        
        layout.addStretch()
        
        self.widgets['guardar_button'] = QPushButton("Guardar Configuración")
        self.widgets['guardar_button'].clicked.connect(self.save)
        layout.addWidget(self.widgets['guardar_button'])
        
        self.load_initial_values()

    def load_initial_values(self):
        estado, frecuencia = self.user_service.cargar_configuracion_recordatorio()
        self.widgets['activar_recordatorio_checkbox'].setChecked(estado == "on")
        index = self.widgets['tiempo_recordatorio_combobox'].findText(frecuencia)
        if index >= 0:
            self.widgets['tiempo_recordatorio_combobox'].setCurrentIndex(index)

    def save(self):
        estado = "on" if self.widgets['activar_recordatorio_checkbox'].isChecked() else "off"
        frecuencia = self.widgets['tiempo_recordatorio_combobox'].currentText()
        if self.user_service.guardar_configuracion_recordatorio(estado, frecuencia):
            QMessageBox.information(self, "Confirmación", "Configuración guardada correctamente.")
            self.accept()