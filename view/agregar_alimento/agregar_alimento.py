# Agregar_Alimento.py - Convertido a PyQt6 con principios SOLID y mejor espaciado
import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QComboBox,
                             QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from model.util.colores import *
from model.util.mensajes import *
from model.agregar_alimento.alimento_factory import SqliteAlimentoFactory
from model.agregar_alimento.alimento_factory import ApiAlimentoFactory 
from model.agregar_alimento.repositorio_api import ApiAlimentoRepository


class CustomButton(QPushButton):
    """Botón personalizado con estilos similares a CTk"""
    def __init__(self, text, width=245, height=35, bg_color="#2ECC71", 
                 hover_color="#27AE60", text_color="black", corner_radius=20, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {corner_radius}px;
                font-size: 16px;
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


class CustomEntry(QLineEdit):
    """Campo de entrada personalizado"""
    def __init__(self, placeholder="", width=245, height=35, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid #BDC3C7;
                border-radius: 17px;
                padding: 8px 15px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: black;
            }}
            QLineEdit:focus {{
                border-color: #3498DB;
                background-color: white;
            }}
        """)


class CustomComboBox(QComboBox):
    def __init__(self, width=245, height=35, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid #BDC3C7;
                border-radius: 17px;
                padding: 8px 15px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: black;
            }}
            QComboBox:focus {{
                border-color: #3498DB;
                background-color: white;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid #BDC3C7;
                background-color: white;
                selection-background-color: #3498DB;
                margin-top: 5px;
            }}
        """)


class HeaderFrame(QFrame):
    """Frame para headers con estilo personalizado"""
    def __init__(self, width=245, height=35, bg_color="#34495E", parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 17px;
            }}
        """)


class HeaderLabel(QLabel):
    """Label para headers"""
    def __init__(self, text, color="white", font_size=16, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                font-weight: bold;
                background-color: transparent;
                font-family: Arial;
            }}
        """)


class InfoButton(QPushButton):
    """Botón de información personalizado"""
    def __init__(self, text="i", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 18px;
                font-style: italic;
                font-family: 'Times New Roman';
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)


# En agregar_alimento.py

class AgregarAlimentoView(QWidget):
    """Vista responsable únicamente de la interfaz gráfica (SRP)."""
    
    def __init__(self, parent_frame, color, on_agregar_callback, on_ayuda_callback):
        super().__init__()  # CAMBIAR: sin parent_frame aquí
        self.on_agregar_callback = on_agregar_callback
        self.on_ayuda_callback = on_ayuda_callback
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz, usando un QGridLayout para alineación perfecta."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # Márgenes más pequeños 
        self.layout.setSpacing(25) 

        # Header con botón de ayuda
        self._crear_header()
        
        # --- Usaremos un QGridLayout para alinear las columnas ---
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 1) # Columna izquierda
        grid_layout.setColumnStretch(1, 1) # Columna derecha
        grid_layout.setColumnStretch(2, 2) # Columna vacía para centrar
        grid_layout.setHorizontalSpacing(50)  # Más espacio horizontal
        grid_layout.setVerticalSpacing(35)    # Más espacio vertical

        # --- Widgets de la Columna Izquierda ---
        # Header "Agregar Alimentos"
        self.header_nombre = HeaderFrame()
        layout_nombre = QVBoxLayout(self.header_nombre)
        layout_nombre.addWidget(HeaderLabel("Agregar Alimentos"))
        
        # Entry para el nombre del alimento
        self.entry_nombre = CustomEntry(placeholder="Ingrese el nombre del alimento")
        
        # --- Widgets Ocultos de Calorías ---
        self.header_calorias = HeaderFrame()
        layout_calorias = QVBoxLayout(self.header_calorias)
        self.label_cant_calorias = HeaderLabel("Calorías")
        layout_calorias.addWidget(self.label_cant_calorias)
        
        self.entry_calorias = CustomEntry(placeholder="Ingrese las calorías")
        
        # Añadir al grid (fila, columna)
        grid_layout.addWidget(self.header_nombre, 0, 0)
        grid_layout.addWidget(self.entry_nombre, 1, 0)
        grid_layout.addWidget(self.header_calorias, 2, 0)
        grid_layout.addWidget(self.entry_calorias, 3, 0)

        # --- Widgets de la Columna Derecha ---
        self.header_porcion = HeaderFrame()
        layout_porcion = QVBoxLayout(self.header_porcion)
        layout_porcion.addWidget(HeaderLabel("Porción / 100gr"))
        
        self.combo_box = CustomComboBox()
        self.combo_box.addItems(["", "Por porción", "100gr"])
        self.combo_box.currentTextChanged.connect(self.actualizar_interfaz)
        
        self.boton_agregar = CustomButton("Añadir Alimento", width=240, height=50, bg_color="#2ECC71", text_color="black")
        self.boton_agregar.clicked.connect(self.on_agregar_callback)
        
        # Añadir al grid (fila, columna)
        grid_layout.addWidget(self.header_porcion, 0, 1)
        grid_layout.addWidget(self.combo_box, 1, 1)
        grid_layout.addWidget(self.boton_agregar, 3, 1) # Alinear con el entry de calorías

        # Inicialmente, ocultar los widgets dinámicos
        self.header_calorias.hide()
        self.entry_calorias.hide()
        self.boton_agregar.hide()

        self.layout.addLayout(grid_layout)
        self.layout.addStretch(1) # Empuja todo hacia arriba
        self._crear_boton_api()
        self.layout.addStretch(2) # Más espacio abajo
            
    def _crear_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes del layout
        header_layout.addStretch()
        self.boton_ayuda = InfoButton("i")
        self.boton_ayuda.clicked.connect(self.on_ayuda_callback)
        header_layout.addWidget(self.boton_ayuda)
        self.layout.addLayout(header_layout)
        
    def actualizar_interfaz(self, seleccion):
        """Muestra u oculta los widgets según la selección del ComboBox."""
        show_widgets = seleccion in ["Por porción", "100gr"]
        
        self.header_calorias.setVisible(show_widgets)
        self.entry_calorias.setVisible(show_widgets)
        self.boton_agregar.setVisible(show_widgets)
        
        if seleccion == "Por porción":
            self.label_cant_calorias.setText("Calorías por porción")
        elif seleccion == "100gr":
            self.label_cant_calorias.setText("Calorías por 100gr")

    def _crear_boton_api(self):
        api_layout = QHBoxLayout()
        api_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes
        api_layout.addStretch()
        self.api = CustomButton("Buscar Calorías", width=200, height=40, bg_color="#2ECC71", hover_color="#27AE60", text_color="black")
        self.api.clicked.connect(self._abrir_api_calorias)
        api_layout.addWidget(self.api)
        self.layout.addLayout(api_layout)
        
    def _abrir_api_calorias(self):
        webbrowser.open("https://fitia.app/es/calorias-informacion-nutricional/")
    
    def obtener_datos_formulario(self):
        return {
            'nombre': self.entry_nombre.text().strip(),
            'calorias': self.entry_calorias.text().strip(),
            'tipo_porcion': self.combo_box.currentText()
        }
    
    def limpiar_formulario(self):
        self.entry_nombre.clear()
        self.combo_box.setCurrentIndex(0) # Esto disparará 'actualizar_interfaz' y ocultará los campos
        self.entry_calorias.clear()

class Agregar_Alimento(QWidget):
    """
    Controlador principal que coordina la vista, servicios y repositorio.
    Convertido a PyQt6 siguiendo el principio de responsabilidad única (SRP).
    """
    catalogo_alimentos_actualizado = pyqtSignal()
    
    def __init__(self, panel_principal, color, usuario=None):
        super().__init__(panel_principal)
        self.panel_principal = panel_principal
        self.color = color
        self.usuario = usuario if usuario else self._get_current_user()
        
        self._inicializar_dependencias()
        self._crear_vista()

    def _get_current_user(self):
        """Obtiene el usuario actual"""
        try:
            with open('usuario_actual.txt', 'r') as f:
                return f.read().strip()
        except:
            return "usuario_default"
    
    def _inicializar_dependencias(self):
        """Inicializa dependencias usando Factory Method puro"""
        self.factory = ApiAlimentoFactory() 
        self.alimento_service = self.factory.crear_alimento_service(self.usuario)
        self.notification_service = self.factory.crear_notification_service()
        
    def _crear_vista(self):
        """Crea la vista y establece los callbacks"""
        # Layout principal para todo el widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame principal con fondo - CAMBIAR AQUÍ
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: none;
            }
        """)
        
        # AÑADIR ESTA LÍNEA para que el frame use todo el espacio
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(main_frame)
        
        # Crear la vista dentro del frame - CAMBIAR AQUÍ
        self.vista = AgregarAlimentoView(
            parent_frame=main_frame,  # Sigue siendo main_frame
            color=self.color,
            on_agregar_callback=self._manejar_agregar_alimento,
            on_ayuda_callback=self._mostrar_ayuda
        )
        
        # AÑADIR la vista al layout del frame
        frame_layout.addWidget(self.vista)
                
    def _mostrar_mensaje_bienvenida(self):
            """Muestra el mensaje de bienvenida desde el archivo central."""
            info = MENSAJES.get("agregar_alimento", {})
            titulo = info.get("titulo", "Agregar Alimento")
            mensaje = info.get("mensaje_html", "Bienvenido a agregar alimentos.")
            
            QTimer.singleShot(1000, lambda: self._mostrar_mensaje(mensaje, titulo))
                

    def _manejar_agregar_alimento(self):
        """Maneja la lógica de 'agregar' (ahora verificar) un alimento"""
        datos = self.vista.obtener_datos_formulario()
        
        # La verificación de similares ya no es necesaria con la API
        # if tiene_similares and similares: ... (SE PUEDE ELIMINAR ESTE BLOQUE)
        
        # Procesar la "adición" del alimento
        exito, mensaje = self.alimento_service.agregar_alimento(
            datos['nombre'], 
            datos['calorias'], 
            datos['tipo_porcion']
        )
        
        if exito:
            # --- Personalizamos el mensaje de éxito para la nueva lógica ---
            mensaje_exito = (f"¡Éxito! El alimento '{datos['nombre']}' fue encontrado y es válido.\n\n"
                             "Ahora puedes buscarlo y registrarlo en la pestaña 'Registrar Alimento'.")
            self._mostrar_exito("Verificación Exitosa", mensaje_exito)
            self.vista.limpiar_formulario()
            
            # La señal sigue siendo útil por si quieres que otras partes de la UI reaccionen
            self.catalogo_alimentos_actualizado.emit()
            
        else:
            # Personalizamos el mensaje de error
            mensaje_error = f"No se pudo verificar el alimento '{datos['nombre']}'.\n\nMotivo: {mensaje}"
            self._mostrar_error("Error de Verificación", mensaje_error)

    def _confirmar_agregar_con_similares(self, similares: list) -> bool:
        """Confirma si el usuario quiere agregar el alimento a pesar de tener similares"""
        similares_texto = ", ".join(similares[:3])  # Mostrar solo los primeros 3
        mensaje = (f"Existen alimentos con nombres similares:\n{similares_texto}\n\n"
                  "¿Desea continuar agregando este nuevo alimento?")
        
        reply = QMessageBox.question(
            self,
            "Nombres similares encontrados",
            mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def _mostrar_ayuda(self):
        """Muestra la ayuda de la aplicación"""
        mensaje = ("Esta es la pestaña de agregar alimento, para agregar un alimento "
                  "debes insertar el nombre del alimento, las calorías por porción o por 100 gramos.")
        self._mostrar_mensaje(mensaje, "Agregar Alimento")
    
    def _mostrar_mensaje(self, mensaje, titulo):
        """Muestra un mensaje informativo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def _mostrar_error(self, titulo, mensaje):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
    
    def _mostrar_exito(self, titulo, mensaje):
        """Muestra un mensaje de éxito"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def __del__(self):
        """Limpia los recursos al destruir la instancia"""
        if hasattr(self, 'repository'):
            self.repository.cerrar_conexion()