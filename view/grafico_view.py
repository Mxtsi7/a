# view/grafico_view.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor # <-- IMPORTANTE: Añadir QColor

# Importamos los nuevos componentes
from view.widgets.bar_chart_widget import BarChartWidget
from model.database_manager import ChartDataManager

class GraficoView(QWidget):
    """
    La vista principal de la sección de gráficos. Construye la UI y delega la lógica.
    """
    def __init__(self, data_provider: ChartDataManager):
        super().__init__()
        self.data_provider = data_provider
        
        self.data_fetchers = {
            "Consumo de Calorías": self.data_provider.get_calories_data,
            "Consumo de Agua": self.data_provider.get_water_data,
            "Registro de Peso": self.data_provider.get_weight_data
        }
        
        self.init_ui()
        self.update_chart()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #3c3c3c; color: white; }
            QGroupBox { font-weight: bold; border: 1px solid #555; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QComboBox { background-color: #555; border: 1px solid #777; border-radius: 5px; padding: 8px; }
            QPushButton { background-color: #4CAF50; border: none; border-radius: 8px; padding: 10px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Gráficos y Estadísticas")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Hacemos el título un poco menos dominante
        title.setFixedHeight(50)
        layout.addWidget(title)
        
        controls_layout = QHBoxLayout()
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Última semana", "Último mes", "Últimos 3 meses", "Último año"])
        
        self.data_combo = QComboBox()
        self.data_combo.addItems(["Consumo de Calorías", "Consumo de Agua", "Registro de Peso"])
        
        self.update_btn = QPushButton("Actualizar")
        
        controls_layout.addWidget(QLabel("Período:"))
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(QLabel("Datos:"))
        controls_layout.addWidget(self.data_combo)
        controls_layout.addWidget(self.update_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.update_btn.clicked.connect(self.update_chart)
        self.data_combo.currentTextChanged.connect(self.update_chart)
        self.period_combo.currentTextChanged.connect(self.update_chart)
        
        self.chart_group = QGroupBox("Estadísticas")
        chart_layout = QVBoxLayout(self.chart_group)
        self.main_chart = BarChartWidget()
        chart_layout.addWidget(self.main_chart)
        
        # El layout principal ahora tiene el gráfico
        layout.addWidget(self.chart_group)

    def update_chart(self):
        """Actualiza el gráfico llamando al proveedor de datos."""
        periodo = self.period_combo.currentText()
        tipo_dato = self.data_combo.currentText()
        
        self.chart_group.setTitle(tipo_dato)
        
        fetch_function = self.data_fetchers.get(tipo_dato)
        
        if fetch_function:
            labels, data = fetch_function(period=periodo)
            
            # --- SOLUCIÓN A LOS COLORES: Paleta temática ---
            color = QColor("#FF9800") # Naranja para Calorías por defecto
            if tipo_dato == "Consumo de Agua":
                color = QColor("#03A9F4") # Azul para Agua
            elif tipo_dato == "Registro de Peso":
                color = QColor("#9C27B0") # Púrpura para Peso
            # -----------------------------------------------

            self.main_chart.set_bar_color(color)
            self.main_chart.set_data(data, labels)