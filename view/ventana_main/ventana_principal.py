#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal del Contador de Calorías con Login integrado
"""
# Se elimina la importación de 'sqlite3'
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from model.database_manager import ChartDataManager
from view.grafico_view import GraficoView
from ..sidebar import Sidebar
from .welcome_screen import WelcomeScreen
from ..menu import Menu
from view.salud.salud import Salud
from controller.configuracion.configuracion import ConfigUI
from view.login.login_form import LoginForm
from view.login.iniciar_sesion_form import IniciarSesionForm
from view.login.registro_form import RegistroForm
from model.login.auth_service import ApiService
# Se elimina la importación de 'UserDatabase' y 'DBManager' que manejaban DB locales
from view.agregar_alimento.agregar_alimento import Agregar_Alimento
from controller.registrar_alimento.registrar_alimento import RegistroAlimentoPyQt6
from controller.historial.historial import Historial

class LoginScreen(QWidget):
    """
    Pantalla de login que se muestra antes de acceder a la aplicación principal.
    Gestiona el cambio entre los formularios de bienvenida, inicio de sesión y registro.
    """
    login_successful = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.auth_service = ApiService()
        # Se elimina la instancia de UserDatabase
        
        self.login_form = None
        self.iniciar_sesion_form = None
        self.registro_form = None

        # Limpiar sesión de usuario al iniciar, usando el nuevo método 'logout'
        self.auth_service.logout()
        self.init_ui()

    def init_ui(self):
        """Inicializar la interfaz de login"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #2b2b2b, stop:1 #3c3c3c);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.form_stack = QStackedWidget(self)

        self.login_form = LoginForm(self, self.auth_service, self.on_login_success)
        self.login_form.iniciar_sesion_clicked.connect(self.mostrar_iniciar_sesion)
        self.login_form.registrarse_clicked.connect(self.mostrar_registro)

        self.form_stack.addWidget(self.login_form)
        layout.addWidget(self.form_stack)

    def mostrar_iniciar_sesion(self):
        """Crea (si no existe) y muestra el formulario de inicio de sesión."""
        if not self.iniciar_sesion_form:
            self.iniciar_sesion_form = IniciarSesionForm(self, self.auth_service, self.on_login_success, None)
            self.iniciar_sesion_form.volver_clicked.connect(self.mostrar_menu_login)
            self.form_stack.addWidget(self.iniciar_sesion_form)

        # --- MODIFICACIÓN CLAVE ---
        # Se eliminan las líneas que intentaban poblar un ComboBox de usuarios,
        # ya que el nuevo formulario usa un QLineEdit y la API no expone la lista de usuarios.
        
        self.form_stack.setCurrentWidget(self.iniciar_sesion_form)

    def mostrar_registro(self):
        """Crea (si no existe) y muestra el formulario de registro."""
        if not self.registro_form:
            # --- MODIFICACIÓN CLAVE ---
            # Cuando el registro es exitoso, se llama a on_login_success directamente,
            # ya que el formulario de registro ahora maneja el auto-login.
            self.registro_form = RegistroForm(self, self.auth_service, self.on_login_success, None)
            
            self.registro_form.volver_clicked.connect(self.mostrar_menu_login)
            self.form_stack.addWidget(self.registro_form)

        self.form_stack.setCurrentWidget(self.registro_form)

    def mostrar_menu_login(self):
        """Vuelve a mostrar el formulario de login principal."""
        self.form_stack.setCurrentWidget(self.login_form)

    def on_login_success(self):
        """Callback cuando el login es exitoso. Emite la señal final."""
        # Se asume que ApiService tiene un método para obtener el usuario actual
        # que fue guardado durante el login.
        usuario_actual = self.auth_service.obtener_usuario_actual()
        if usuario_actual:
            self.login_successful.emit(usuario_actual)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.is_logged_in = False
        # Se elimina la caché de mensajes de bienvenida, ya que la funcionalidad se ha quitado.
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        self.init_login()
        self.init_main_ui()
        
        self.show_login()

    # --- MODIFICACIÓN CLAVE ---
    # Los métodos 'check_message_status' y 'update_message_status' han sido eliminados
    # porque dependían de una base de datos local por usuario.

    def init_login(self):
        """Inicializar la pantalla de login"""
        self.login_screen = LoginScreen(self)
        self.login_screen.login_successful.connect(self.on_login_success)
        self.main_stack.addWidget(self.login_screen)
        
    def init_main_ui(self):
        """Inicializar la interfaz principal (después del login)"""
        self.main_widget = QWidget()
        self.main_stack.addWidget(self.main_widget)
        
        self.setWindowTitle("Contador de Calorías Pro 60Hz")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
        """)
        
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = None
        self.content_area = None
        
    def setup_main_interface(self):
        """Configurar la interfaz principal después del login exitoso"""
        layout = self.main_widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        self.sidebar = Sidebar()
        self.sidebar.section_changed.connect(self.change_section)
        
        self.content_area = self.create_content_area()
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area, 1)
        
        self.setup_timer()
        
    def create_content_area(self):
        """Crear el área de contenido principal"""
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background-color: #3c3c3c; border-left: 2px solid #4a4a4a; }")
        
        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #3c3c3c;")
        
        self.welcome_screen = WelcomeScreen()
        self.registrar_alimento = RegistroAlimentoPyQt6(usuario=self.current_user)
        self.agregar_alimento = Agregar_Alimento(panel_principal=self.stacked_widget, color="#3c3c3c", usuario=self.current_user)
        self.data_manager = ChartDataManager(username=self.current_user)
        self.graficos_view = GraficoView(data_provider=self.data_manager)
        self.historial = Historial(panel_principal=self.stacked_widget, color="#3c3c3c", usuario=self.current_user)
        self.settings = ConfigUI(self, "#3c3c3c", self.current_user)
        self.salud = Salud()
        self.menu = Menu()
        
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.registrar_alimento)
        self.stacked_widget.addWidget(self.agregar_alimento)
        self.stacked_widget.addWidget(self.graficos_view)
        self.stacked_widget.addWidget(self.historial)
        self.stacked_widget.addWidget(self.settings)
        self.stacked_widget.addWidget(self.salud)
        self.stacked_widget.addWidget(self.menu)
        
        layout.addWidget(self.stacked_widget)
        self.conectar_modulos()

        return content_frame
    
    def conectar_modulos(self):
        """Conecta las señales de los diferentes módulos a los slots de otros."""
        print("Realizando conexiones entre módulos...")
        if hasattr(self.agregar_alimento, 'catalogo_alimentos_actualizado') and hasattr(self.registrar_alimento, 'refrescar_lista_alimentos'):
            self.agregar_alimento.catalogo_alimentos_actualizado.connect(self.registrar_alimento.refrescar_lista_alimentos)
            print("CONEXIÓN CREADA: Agregar Alimento -> Registrar Alimento (ComboBox)")
        if hasattr(self.registrar_alimento, 'consumo_diario_actualizado'):
            if hasattr(self.historial, 'refrescar_vista'):
                self.registrar_alimento.consumo_diario_actualizado.connect(self.historial.refrescar_vista)
                print("CONEXIÓN CREADA: Registrar Alimento -> Historial")
            if hasattr(self.salud, 'refrescar_vista'):
                self.registrar_alimento.consumo_diario_actualizado.connect(self.salud.refrescar_vista)
                print("CONEXIÓN CREADA: Registrar Alimento -> Salud")
        if hasattr(self.settings, 'datos_usuario_actualizados') and hasattr(self.salud, 'refrescar_vista'):
            self.settings.datos_usuario_actualizados.connect(self.salud.refrescar_vista)
            print("CONEXIÓN CREADA: Configuración -> Salud")
        if hasattr(self.salud, 'datos_usuario_actualizados') and hasattr(self.settings, 'refrescar_vista'):
            self.salud.datos_usuario_actualizados.connect(self.settings.refrescar_vista)
            print("CONEXIÓN CREADA: Salud -> Configuración")

    def create_header(self):
        """Crear la barra superior"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("QFrame { background-color: #2b2b2b; border-bottom: 2px solid #4a4a4a; }")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        title_label = QLabel("Contador de Calorías")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        user_label = QLabel(f"Usuario: {self.current_user}")
        user_label.setFont(QFont("Arial", 12))
        user_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(title_label)
        layout.addWidget(user_label)
        layout.addStretch()
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Arial", 12))
        self.datetime_label.setStyleSheet("color: #cccccc;")
        self.update_datetime()
        layout.addWidget(self.datetime_label)
        return header
    
    def setup_timer(self):
        """Configurar el timer para actualizar fecha/hora"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
    
    def update_datetime(self):
        """Actualizar la fecha y hora en la interfaz"""
        now = datetime.now()
        formatted_date = now.strftime("Hoy es: %d-%m-%Y")
        if hasattr(self, 'datetime_label'):
            self.datetime_label.setText(formatted_date)
    
    def show_login(self):
        """Mostrar la pantalla de login"""
        self.main_stack.setCurrentWidget(self.login_screen)
        self.is_logged_in = False
    
    def show_main(self):
        """Mostrar la interfaz principal"""
        self.main_stack.setCurrentWidget(self.main_widget)
        self.is_logged_in = True
    
    def on_login_success(self, username):
        """Callback cuando el login es exitoso"""
        self.current_user = username
        self.setup_main_interface() 
        self.sidebar.set_usuario(self.current_user)
        self.show_main()
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        self.current_user = None
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        if hasattr(self.login_screen, 'auth_service'):
            # Se actualiza la llamada al nuevo método 'logout'
            self.login_screen.auth_service.logout()
        
        self.show_login()
    
    def change_section(self, section_name):
        """Cambiar de sección y mostrar mensaje de bienvenida una sola vez."""
        if not self.is_logged_in:
            return
            
        # --- MODIFICACIÓN CLAVE ---
        # Se elimina toda la lógica de mensajes de bienvenida que dependía de la BD local.
        # Ahora, simplemente cambiamos de vista.
        
        section_map = {
            "welcome": 0, "registrar": 1, "agregar": 2, "grafico": 3,
            "historial": 4, "settings": 5, "salud": 6, "menu": 7
        }
        
        if section_name in section_map:
            self.stacked_widget.setCurrentIndex(section_map[section_name])
                                                    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()