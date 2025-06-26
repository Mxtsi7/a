from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFrame, QScrollArea, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from model.login.user_validator import UserValidator
from model.login.auth_service import ApiService
from model.util.colores import *
from .form import *

class RegistroForm(IForm, QWidget):

    volver_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: ApiService, on_success, on_back):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_back = on_back
        self.widgets = {}
        self.validator = UserValidator()
        self.init_ui()
        
    def init_ui(self):
        # La UI no cambia, solo la lógica de guardado.
        # El código de init_ui se mantiene idéntico al original.
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.frame = QFrame()
        self.frame.setStyleSheet(f"background-color: {gris}; border-radius: 15px; padding: 20px;")
        self.frame.setFixedSize(450, 620)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(15)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        titulo = QLabel("Crear una Cuenta")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {color_texto_blanco}; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"QScrollArea {{ background-color: transparent; border: none; }} QScrollBar:vertical {{ background-color: {azul_medio_oscuro}; width: 12px; margin: 0px; border-radius: 6px; }} QScrollBar::handle:vertical {{ background-color: {verde_boton}; min-height: 20px; border-radius: 6px; }} QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; border: none; }}")
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 0, 5, 0)
        label_style = f"QLabel {{ background-color: {azul_medio_oscuro}; color: {color_texto_blanco}; font: bold 13px Arial; border-radius: 15px; padding: 8px; min-height: 20px; }}"
        input_style = f"QLineEdit, QComboBox, QDateEdit {{ background-color: {color_entry}; color: {negro_texto}; border-radius: 15px; padding: 8px 12px; font: 13px Arial; min-height: 20px; }} QComboBox::drop-down {{ background-color: {celeste_pero_oscuro}; border-top-right-radius: 15px; border-bottom-right-radius: 15px; width: 25px; }}"
        campos = {"Nombre": ("nombre_entry", QLineEdit(), "Introduce tu nombre"), "Contraseña": ("contra_entry", QLineEdit(), "Crea una contraseña segura"), "Genero": ("gen_combobox", QComboBox(), None), "Peso (kg)": ("peso_entry", QLineEdit(), "Tu peso actual en kilogramos"), "Altura (cm)": ("altura_entry", QLineEdit(), "Tu altura en centímetros"), "Meta de calorías diaria": ("meta_entry", QLineEdit(), "Ej: 2000 kcal"), "Nivel de Actividad": ("lvl_actividad_combobox", QComboBox(), None), "Fecha de Nacimiento": ("fecha_nacimiento_entry", QDateEdit(), None)}
        for label_text, (widget_name, widget_instance, placeholder) in campos.items():
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(label)
            self.widgets[widget_name] = widget_instance
            widget_instance.setStyleSheet(input_style)
            if isinstance(widget_instance, QLineEdit): widget_instance.setPlaceholderText(placeholder)
            if widget_name == "contra_entry": widget_instance.setEchoMode(QLineEdit.EchoMode.Password)
            if widget_name == "gen_combobox": widget_instance.addItems(["Masculino", "Femenino"])
            if widget_name == "lvl_actividad_combobox": widget_instance.addItems(["Sedentario", "Ligero", "Moderado", "Intenso"])
            if isinstance(widget_instance, QDateEdit):
                widget_instance.setCalendarPopup(True)
                widget_instance.setDate(QDate.currentDate().addYears(-25))
                widget_instance.setDateRange(QDate.currentDate().addYears(-120), QDate.currentDate().addYears(-13))
                widget_instance.setDisplayFormat("dd/MM/yyyy")
            scroll_layout.addWidget(widget_instance)
        scroll_area.setWidget(scroll_widget)
        frame_layout.addWidget(scroll_area)
        self.widgets['guardar_button'] = QPushButton("Crear Cuenta")
        self.widgets['guardar_button'].setStyleSheet(f"QPushButton {{ background-color: {verde_boton}; color: {color_texto_blanco}; border: none; border-radius: 15px; font: bold 14px Arial; padding: 12px; }} QPushButton:hover {{ background-color: {verde_oscuro}; }}")
        self.widgets['guardar_button'].clicked.connect(self._guardar)
        frame_layout.addWidget(self.widgets['guardar_button'])
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        self.widgets['btn_volver'].setStyleSheet(f"QPushButton {{ background-color: {riesgo_medio}; color: {color_texto_blanco}; border: none; border-radius: 15px; font: bold 14px Arial; padding: 12px; }} QPushButton:hover {{ background-color: {riesgo_alto}; }}")
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        frame_layout.addWidget(self.widgets['btn_volver'])
        main_layout.addWidget(self.frame)

    def mostrar(self):
        self.show()
    
    def ocultar(self):
        self.hide()
    
    def _volver_atras(self):
        self.volver_clicked.emit()

    def _guardar(self):
        # 1. Validación del lado del cliente (sin cambios)
        nombre = self.widgets['nombre_entry'].text()
        valid_nombre, msg_nombre = UserValidator.validar_nombre(nombre)
        if not valid_nombre:
            QMessageBox.warning(self, "Advertencia", msg_nombre)
            return
        
        contra = self.widgets['contra_entry'].text()
        valid_contra, msg_contra = UserValidator.validar_contraseña(contra, nombre)
        if not valid_contra:
            QMessageBox.warning(self, "Advertencia", msg_contra)
            return
        
        fecha_qdate = self.widgets['fecha_nacimiento_entry'].date()
        fecha_str_validator = fecha_qdate.toString("dd-MM-yyyy")
        valid_fecha, resultado_fecha = UserValidator.validar_fecha_nacimiento(fecha_str_validator)
        if not valid_fecha:
            QMessageBox.warning(self, "Advertencia", resultado_fecha)
            return
        
        valid_peso, peso = UserValidator.validar_numero(self.widgets['peso_entry'].text(), "peso")
        if not valid_peso: QMessageBox.warning(self, "Advertencia", peso); return
        
        valid_altura, estatura = UserValidator.validar_numero(self.widgets['altura_entry'].text(), "altura")
        if not valid_altura: QMessageBox.warning(self, "Advertencia", estatura); return
        
        # ... (Validación de IMC se mantiene)
        if peso and estatura:
            try:
                imc = peso / ((estatura / 100) ** 2)
                if imc < 10 or imc > 60:
                    reply = QMessageBox.question(self, "IMC inusual", f"El IMC calculado es {imc:.2f}, lo cual parece poco realista.\n¿Estás seguro?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No: return
            except ZeroDivisionError:
                QMessageBox.warning(self, "Advertencia", "La altura no puede ser cero."); return

        valid_meta, meta_cal = UserValidator.validar_numero(self.widgets['meta_entry'].text(), "meta de calorías")
        if not valid_meta: QMessageBox.warning(self, "Advertencia", meta_cal); return
        
        # 2. Construir el payload para la API
        user_data = {
            "nombre_usuario": nombre,
            "password": contra,
            "genero": self.widgets['gen_combobox'].currentText(),
            "peso": float(peso),
            "altura": int(estatura),
            "meta_calorias": int(meta_cal),
            "nivel_actividad": self.widgets['lvl_actividad_combobox'].currentText(),
            "fecha_nacimiento": fecha_qdate.toString("yyyy-MM-dd") # Formato para Pydantic
        }

        # 3. Llamar a la API para registrar
        try:
            success, message = self.auth_service.register(user_data)
            
            if not success:
                QMessageBox.critical(self, "Error de Registro", message)
                return

            QMessageBox.information(self, "Éxito", "Se ha registrado correctamente. Iniciando sesión...")
            
            # 4. Iniciar sesión automáticamente
            login_success, login_message = self.auth_service.login(nombre, contra)
            if login_success:
                self.ocultar()
                self.on_success()
            else:
                QMessageBox.warning(self, "Error de Sesión", f"Registro exitoso, pero no se pudo iniciar sesión. Por favor, inténtelo manualmente.\nError: {login_message}")
                self.volver_clicked.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado: {str(e)}")