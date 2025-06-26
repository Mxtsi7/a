# view/widgets/bar_chart_widget.py

from PyQt6.QtWidgets import QWidget, QSizePolicy # <-- IMPORTANTE: Añadir QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QColor

class BarChartWidget(QWidget):
    """Widget especializado en dibujar un gráfico de barras con ejes."""
    def __init__(self):
        super().__init__()
        self.data = []
        self.labels = []
        
        # --- SOLUCIÓN AL TAMAÑO: Le decimos al widget que se expanda verticalmente ---
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.bar_color = QColor("#00bcd4") # Color cian por defecto

    def set_data(self, data, labels):
        self.data = data
        self.labels = labels
        self.update()

    def set_bar_color(self, color: QColor):
        """Establece el color de las barras del gráfico."""
        self.bar_color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#3c3c3c")) # Fondo consistente con tu UI

        if not self.data:
            painter.setPen(QColor("#ffffff"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No hay datos para mostrar")
            return

        self.draw_bar_chart(painter)

    def draw_bar_chart(self, painter):
        margin_top, margin_bottom, margin_right, margin_left = 50, 50, 50, 80
        
        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom
        
        max_value = max(self.data) if self.data else 1
        
        # --- MEJORA ESTÉTICA: Lógica para que las barras no sean demasiado anchas ---
        num_bars = len(self.data) if len(self.data) > 0 else 1
        # Calculamos el ancho ideal pero lo limitamos a un máximo de 60px
        bar_width = min(60, chart_width // num_bars)
        # Centramos el grupo de barras si no ocupan todo el ancho
        total_bars_width = num_bars * bar_width
        x_offset = (chart_width - total_bars_width) / 2
        # --- FIN DE LA MEJORA ---
        
        # --- DIBUJAR EJE Y ---
        painter.setPen(QPen(QColor("#ffffff")))
        num_labels = 5
        for i in range(num_labels + 1):
            value = max_value * (i / num_labels)
            y = self.height() - margin_bottom - (i * (chart_height / num_labels))
            
            painter.setPen(QPen(QColor("#666666"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(margin_left, int(y), self.width() - margin_right, int(y))
            
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawText(0, int(y - 10), margin_left - 10, 20, 
                           Qt.AlignmentFlag.AlignRight, f"{int(value)}")

        # --- DIBUJAR BARRAS Y EJE X ---
        bar_fill_color = QBrush(self.bar_color)
        
        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            x = margin_left + x_offset + i * bar_width # <-- Usamos el offset
            y = self.height() - margin_bottom - bar_height
            
            painter.setBrush(bar_fill_color)
            painter.setPen(Qt.PenStyle.NoPen) 
            painter.drawRect(int(x + 5), int(y), int(bar_width - 10), int(bar_height))
            
            painter.setPen(QColor("#ffffff"))
            if i < len(self.labels):
                painter.drawText(int(x), self.height() - margin_bottom + 5, int(bar_width), 20, 
                               Qt.AlignmentFlag.AlignCenter, self.labels[i])