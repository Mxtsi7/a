from PyQt6.QtWidgets import QSlider, QLabel
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont
from datetime import datetime

class TiempoManager:
    def __init__(self, parent):
        self.parent = parent
        self.hour_value = datetime.now().hour
        self.minute_value = datetime.now().minute
        self.time_label = None
        self.hour_slider = None
        self.minute_slider = None
        self.create_sliders()

    def create_sliders(self):
        # Slider para horas
        self.hour_slider = QSlider(Qt.Orientation.Horizontal, self.parent)
        self.hour_slider.setRange(0, 23)
        self.hour_slider.setValue(self.hour_value)
        self.hour_slider.valueChanged.connect(self.update_hour)
        
        # Slider para minutos
        self.minute_slider = QSlider(Qt.Orientation.Horizontal, self.parent)
        self.minute_slider.setRange(0, 59)
        self.minute_slider.setValue(self.minute_value)
        self.minute_slider.valueChanged.connect(self.update_minute)
        
        # Label para mostrar la hora
        self.time_label = QLabel(self.parent)
        self.time_label.setFont(QFont("Arial", 16))
        self.time_label.setStyleSheet("color: white;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.position_widgets()
        self.update_time_label()

    def position_widgets(self):
        """Posiciona los widgets usando coordenadas relativas"""
        parent_width = self.parent.width()
        parent_height = self.parent.height()
        
        # Posicionar slider de horas
        hour_x = int(parent_width * 0.5)
        hour_y = int(parent_height * 0.55)
        hour_width = int(parent_width * 0.18)
        self.hour_slider.setGeometry(QRect(hour_x, hour_y, hour_width, 30))
        
        # Posicionar slider de minutos
        minute_x = int(parent_width * 0.72)
        minute_y = int(parent_height * 0.55)
        minute_width = int(parent_width * 0.18)
        self.minute_slider.setGeometry(QRect(minute_x, minute_y, minute_width, 30))
        
        # Posicionar label de tiempo
        label_x = int(parent_width * 0.5)
        label_y = int(parent_height * 0.60)
        label_width = int(parent_width * 0.4)
        label_height = int(parent_height * 0.05)
        self.time_label.setGeometry(QRect(label_x, label_y, label_width, label_height))

    def update_hour(self, value):
        """Actualiza el valor de la hora"""
        self.hour_value = value
        self.update_time_label()

    def update_minute(self, value):
        """Actualiza el valor de los minutos"""
        self.minute_value = value
        self.update_time_label()

    def update_time_label(self):
        """Actualiza el texto del label con la hora actual"""
        time_text = f"{self.hour_value:02}:{self.minute_value:02}"
        self.time_label.setText(time_text)

    def set_current_time(self):
        """Establece la hora actual en los sliders"""
        now = datetime.now()
        self.hour_value = now.hour
        self.minute_value = now.minute
        self.hour_slider.setValue(self.hour_value)
        self.minute_slider.setValue(self.minute_value)
        self.update_time_label()

    def get_time(self):
        """Devuelve la hora seleccionada en formato HH:MM"""
        return f"{self.hour_value:02}:{self.minute_value:02}"

    def resizeEvent(self):
        """Método para reposicionar widgets cuando cambia el tamaño de la ventana"""
        if self.hour_slider and self.minute_slider and self.time_label:
            self.position_widgets()