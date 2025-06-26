from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject

class ResultDisplay(QObject):
    """Clase responsable de mostrar los resultados finales"""
    
    def __init__(self, parent=None):
        """
        Inicializa el display de resultados
        
        Args:
            parent: Widget padre para los diálogos
        """
        super().__init__()
        self.parent = parent
    
    def show_result_message(self, bpm, evaluation_message):
        """
        Muestra un mensaje de resultado con el BPM y la evaluación
        
        Args:
            bpm (int): El valor final de BPM
            evaluation_message (str): Mensaje de evaluación del pulso
        """
        message = f"Pulsaciones finales: {bpm}\n{evaluation_message}"
        
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("Resultado del Entrenamiento")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()