from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class PulseUIBuilder:
    """Clase responsable de construir y actualizar la interfaz de usuario para la medición de pulso"""
    
    def __init__(self, parent_frame, on_button_click_callback):
        """
        Inicializa el constructor de UI
        
        Args:
            parent_frame: El widget padre donde se colocarán los componentes
            on_button_click_callback: Función callback para el botón de pulso
        """
        self.parent = parent_frame
        self.on_button_click = on_button_click_callback
        self.ui_components = {}
        self.layout = QVBoxLayout(self.parent)
    
    def build_ui(self):
        """Construye todos los componentes de la interfaz de usuario"""
        self._create_instruction_label()
        self._create_counter_label()
        self._create_bpm_label()
        self._create_pulse_button()
        return self.ui_components
    
    def _create_instruction_label(self):
        """Crea la etiqueta de instrucciones"""
        instruction_label = QLabel("Haga clic para medir su pulso")
        instruction_label.setFont(QFont("Arial", 20))
        instruction_label.setStyleSheet("color: white; min-width: 200px;")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setContentsMargins(0, 20, 0, 10)
        
        self.layout.addWidget(instruction_label)
        self.ui_components["instruction_label"] = instruction_label
    
    def _create_counter_label(self):
        """Crea la etiqueta del contador de clicks"""
        counter_label = QLabel("Contador: 10")
        counter_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        counter_label.setStyleSheet("""
            background-color: #2B5F75;
            color: white;
            border-radius: 20px;
            padding: 10px;
        """)
        counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        counter_label.setContentsMargins(0, 10, 0, 10)
        
        self.layout.addWidget(counter_label)
        self.ui_components["counter_label"] = counter_label
    
    def _create_bpm_label(self):
        """Crea la etiqueta para mostrar los BPM"""
        bpm_label = QLabel("BPM: N/A")
        bpm_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        bpm_label.setStyleSheet("""
            background-color: #2B5F75;
            color: white;
            border-radius: 20px;
            padding: 10px;
        """)
        bpm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bpm_label.setContentsMargins(0, 10, 0, 10)
        
        self.layout.addWidget(bpm_label)
        self.ui_components["bpm_label"] = bpm_label
    
    def _create_pulse_button(self):
        """Crea el botón circular para registrar el pulso"""
        circle_button = QPushButton("")
        circle_button.setFixedSize(QSize(100, 100))
        circle_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        circle_button.clicked.connect(self.on_button_click)
        
        # Centramos el botón
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.addWidget(circle_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.setContentsMargins(0, 50, 0, 0)
        
        self.layout.addWidget(button_widget)
        self.ui_components["circle_button"] = circle_button
    
    def update_counter_label(self, counter_value):
        """
        Actualiza el texto de la etiqueta del contador
        
        Args:
            counter_value (int): El valor actual del contador
        """
        self.ui_components["counter_label"].setText(f"Contador: {counter_value}")
    
    def update_bpm_label(self, bpm_value):
        """
        Actualiza el texto de la etiqueta de BPM
        
        Args:
            bpm_value (int): El valor actual de BPM
        """
        self.ui_components["bpm_label"].setText(f"BPM: {bpm_value}")