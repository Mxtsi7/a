from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from model.util.colores import *
from model.pulsaciones.pulse_calculator import PulseCalculator
from model.pulsaciones.pulse_evaluator import PulseEvaluator
from view.pulsaciones.pulse_ui_components import PulseUIBuilder
from view.pulsaciones.result_display import ResultDisplay

class Pulsaciones(QDialog):
    """Ventana principal para la medición de pulsaciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._configure_window()
        
        # Inicializar servicios
        self.pulse_calculator = PulseCalculator()
        self.pulse_evaluator = PulseEvaluator()
        self.result_display = ResultDisplay(self)
        
        # Configurar la interfaz
        self._setup_ui()
        
    def _configure_window(self):
        """Configura las propiedades de la ventana"""
        self.setFixedSize(400, 400)
        self.setWindowTitle('Medidor de Pulso')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.setModal(True)
        
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame principal con color de fondo
        self.main_frame = QWidget()
        self.main_frame.setStyleSheet(f"background-color: {gris};")  # Usando el color importado
        
        # Construir la interfaz de usuario
        self.ui_builder = PulseUIBuilder(
            self.main_frame, 
            self.on_pulse_button_click
        )
        self.ui_components = self.ui_builder.build_ui()
        
        # Añadir el frame principal al layout
        main_layout.addWidget(self.main_frame)
        
    def on_pulse_button_click(self):
        """Maneja el evento de click en el botón de pulso"""
        if self.pulse_calculator.remaining_clicks > 0:
            # Registrar click y actualizar contador
            self.pulse_calculator.record_click()
            
            # Actualizar UI con el contador y BPM actuales
            self.ui_builder.update_counter_label(self.pulse_calculator.remaining_clicks)
            current_bpm = self.pulse_calculator.calculate_current_bpm()
            
            if current_bpm is not None:
                self.ui_builder.update_bpm_label(current_bpm)
            
            # Comprobar si hemos terminado
            if self.pulse_calculator.remaining_clicks == 0:
                self._show_final_result()
    
    def _show_final_result(self):
        """Muestra el resultado final después de completar las pulsaciones"""
        final_bpm = self.pulse_calculator.calculate_final_bpm()
        
        if final_bpm is not None:
            evaluation = self.pulse_evaluator.evaluate_pulse(final_bpm)
            self.close()  # Cerrar la ventana de medición
            self.result_display.show_result_message(final_bpm, evaluation)