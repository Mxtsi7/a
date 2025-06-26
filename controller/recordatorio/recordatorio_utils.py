from datetime import datetime
from PyQt6.QtWidgets import QMessageBox

MOSTRADO_HOY = 'mostrado_hoy'
MOSTRADO = 'mostrado'
ON = 'on'
OFF = 'off'

def _mostrar_error(mensaje, parent=None):
    """Muestra un mensaje de error usando QMessageBox"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Error")
    msg_box.setText(mensaje)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

def _debe_mostrar_recordatorio(dias_diferencia, frecuencia_dias, estado, ultimo_msj):
    """Determina si debe mostrar el recordatorio basado en los parámetros"""
    fecha_hoy = datetime.now().date()
    if ultimo_msj and ultimo_msj == fecha_hoy.strftime('%Y-%m-%d'):
        return False  # No mostrar si ya se mostró hoy
    return (dias_diferencia is not None and dias_diferencia >= frecuencia_dias and estado != MOSTRADO_HOY) \
           or estado == MOSTRADO