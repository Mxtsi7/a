from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QComboBox, QLineEdit, QGroupBox,
                             QHeaderView, QAbstractItemView, QMessageBox,
                             QFileDialog, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
import csv

class ModernGroupBox(QGroupBox):
    """GroupBox personalizado con estilo moderno"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            ModernGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 15px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: rgba(76, 175, 80, 0.1);
            }
            ModernGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
            }
        """)

class StatCard(QFrame):
    """Tarjeta de estadística moderna"""
    def __init__(self, title, value="0", icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.value_text = value
        self.icon = icon
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(100)
        self.setStyleSheet("""
            StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 15px;
                border: 2px solid #45a049;
            }
            StatCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valor
        self.value_label = QLabel(self.value_text)
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        
    def update_value(self, value):
        self.value_label.setText(str(value))

class HistorialView(QWidget):
    """Vista moderna del historial con animaciones y mejor UX"""
    
    # Señales para comunicación con el controlador
    filtro_aplicado = pyqtSignal()
    filtros_limpiados = pyqtSignal()
    exportar_solicitado = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.datos_actuales = []
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario moderna"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(76, 175, 80, 0.3);
                border-radius: 10px;
                padding: 12px;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #4CAF50;
                background-color: rgba(255, 255, 255, 0.15);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.05);
                alternate-background-color: rgba(255, 255, 255, 0.1);
                gridline-color: rgba(76, 175, 80, 0.3);
                selection-background-color: rgba(76, 175, 80, 0.4);
                border: 2px solid rgba(76, 175, 80, 0.2);
                border-radius: 15px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                padding: 15px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 15px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 15px;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #4CAF50;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #45a049;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Widget contenedor principal
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)
        
        # Header con título y botón de ayuda
        self.create_header(layout)
        
        # Filtros
        self.create_filters_section(layout)
        
        # Estadísticas
        self.create_statistics_section(layout)
        
        # Tabla
        self.create_table_section(layout)
        
        scroll_area.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
    def create_header(self, layout):
        """Crear header con título y botón de ayuda"""
        header_layout = QHBoxLayout()
        
        # Título principal
        title = QLabel("📊 Historial de Consumo")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("""
            color: white;
            margin-bottom: 10px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(76, 175, 80, 0.3), stop:1 transparent);
            border-radius: 15px;
        """)
        
        # Botón de ayuda moderno
        self.help_button = QPushButton("❓")
        self.help_button.setFixedSize(50, 50)
        self.help_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                transform: scale(1.1);
            }
        """)
        self.help_button.clicked.connect(self.mostrar_ayuda)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.help_button)
        
        layout.addLayout(header_layout)
    
    def create_filters_section(self, layout):
        """Crear sección de filtros moderna"""
        filters_group = ModernGroupBox("🔍 Filtros de Búsqueda")
        filters_layout = QVBoxLayout(filters_group)
        filters_layout.setSpacing(20)
        
        # Primera fila - Fechas
        date_row = QHBoxLayout()
        
        date_label = QLabel("📅 Período:")
        date_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setMinimumWidth(150)
        
        date_separator = QLabel("→")
        date_separator.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setMinimumWidth(150)
        
        date_row.addWidget(date_label)
        date_row.addWidget(self.date_from)
        date_row.addWidget(date_separator)
        date_row.addWidget(self.date_to)
        date_row.addStretch()
        
        # Segunda fila - Búsqueda y filtros
        search_row = QHBoxLayout()
        
        search_label = QLabel("🔍 Buscar:")
        search_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingresa el nombre del alimento...")
        self.search_input.setMinimumWidth(200)
        
        meal_label = QLabel("🍽️ Momento:")
        meal_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        self.meal_filter = QComboBox()
        self.meal_filter.addItems(["Todos", "Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena", "Otro"])
        self.meal_filter.setMinimumWidth(150)
        
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input)
        search_row.addWidget(meal_label)
        search_row.addWidget(self.meal_filter)
        search_row.addStretch()
        
        # Tercera fila - Botones de acción
        buttons_row = QHBoxLayout()
        
        self.filter_btn = QPushButton("🔄 Aplicar Filtros")
        self.filter_btn.clicked.connect(self.filtro_aplicado.emit)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Filtros")
        self.clear_btn.clicked.connect(self.limpiar_filtros)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:1 #d32f2f);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #b71c1c);
            }
        """)
        
        self.export_btn = QPushButton("📥 Exportar CSV")
        self.export_btn.clicked.connect(self.exportar_solicitado.emit)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        
        buttons_row.addWidget(self.filter_btn)
        buttons_row.addWidget(self.clear_btn)
        buttons_row.addWidget(self.export_btn)
        buttons_row.addStretch()
        
        filters_layout.addLayout(date_row)
        filters_layout.addLayout(search_row)
        filters_layout.addLayout(buttons_row)
        
        layout.addWidget(filters_group)
    
    def create_statistics_section(self, layout):
        """Crear sección de estadísticas con tarjetas modernas"""
        stats_group = ModernGroupBox("📈 Estadísticas del Período")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)
        
        # Crear tarjetas de estadísticas
        self.calories_card = StatCard("Calorías Totales", "0", "🔥")
        self.foods_card = StatCard("Alimentos", "0", "🍎")
        self.average_card = StatCard("Promedio Diario", "0", "📊")
        
        stats_layout.addWidget(self.calories_card)
        stats_layout.addWidget(self.foods_card)
        stats_layout.addWidget(self.average_card)
        stats_layout.addStretch()
        
        layout.addWidget(stats_group)
    
    def create_table_section(self, layout):
        """Crear sección de tabla moderna"""
        table_group = ModernGroupBox("📋 Registro de Consumos")
        table_layout = QVBoxLayout(table_group)
        
        self.create_table()
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_group)
    
    def create_table(self):
        """Crear la tabla de historial moderna"""
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        headers = ["🍎 Alimento", "📂 Tipo", "⚖️ Cantidad", "🔥 Calorías", "📅 Fecha", "🕐 Hora", "🍽️ Momento"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configurar la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        # Configurar el ancho de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Alimento
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Calorías
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Hora
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Momento
        
        # Hacer que las filas sean más altas
        self.table.verticalHeader().setDefaultSectionSize(40)
    
    def setup_animations(self):
        """Configurar animaciones"""
        # Animación para el botón de ayuda
        self.help_animation = QPropertyAnimation(self.help_button, b"geometry")
        self.help_animation.setDuration(200)
        self.help_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def update_table_data(self, registros):
        """Actualizar datos de la tabla con estilo mejorado"""
        self.datos_actuales = registros
        self.table.setRowCount(len(registros))
        
        for row, registro in enumerate(registros):
            # Crear items con estilos
            items = [
                QTableWidgetItem(str(registro[0])),  # nombre
                QTableWidgetItem(str(registro[1])),  # tipo
                QTableWidgetItem(str(registro[2])),  # cantidad
                QTableWidgetItem(str(registro[3])),  # calorias
                QTableWidgetItem(str(registro[4])),  # fecha
                QTableWidgetItem(str(registro[5])),  # hora
                QTableWidgetItem(str(registro[6]))   # momento
            ]
            
            # Aplicar estilos especiales a ciertas columnas
            for col, item in enumerate(items):
                if col == 3:  # Columna de calorías
                    calorias = int(registro[3])
                    if calorias > 300:
                        item.setBackground(QColor(255, 87, 34, 50))  # Naranja para altas calorías
                    elif calorias > 150:
                        item.setBackground(QColor(255, 193, 7, 50))  # Amarillo para calorías medias
                    else:
                        item.setBackground(QColor(76, 175, 80, 50))  # Verde para bajas calorías
                
                self.table.setItem(row, col, item)
    
    def update_statistics_display(self, estadisticas):
        """Actualizar display de estadísticas con animación"""
        self.calories_card.update_value(f"{estadisticas['total_calorias']:,.0f}")
        self.foods_card.update_value(str(estadisticas['total_alimentos']))
        self.average_card.update_value(f"{estadisticas['promedio_diario']:.0f}")
    
    def show_error_message(self, mensaje):
        """Mostrar mensaje de error con estilo"""
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Error")
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        msg.exec()
    
    def mostrar_ayuda(self):
        """Mostrar mensaje de ayuda con estilo mejorado"""
        msg = QMessageBox(self)
        msg.setWindowTitle("💡 Ayuda - Historial")
        msg.setText("""
        <h3>🔍 Historial de Consumo</h3>
        <p>Esta pestaña te permite revisar tu historial completo de consumo de alimentos.</p>
        
        <h4>📋 Funcionalidades:</h4>
        <ul>
        <li><b>📅 Filtros de fecha:</b> Selecciona un rango de fechas específico</li>
        <li><b>🔍 Búsqueda:</b> Encuentra alimentos por nombre</li>
        <li><b>🍽️ Filtro por momento:</b> Ve qué comiste en desayuno, almuerzo, etc.</li>
        <li><b>📊 Estadísticas:</b> Visualiza tus totales y promedios</li>
        <li><b>📥 Exportar:</b> Descarga tus datos en formato CSV</li>
        </ul>
        
        <h4>💡 Consejos:</h4>
        <p>• Usa los filtros para encontrar patrones en tu alimentación<br>
        • Las calorías se colorean según su valor (verde=bajo, amarillo=medio, naranja=alto)<br>
        • Puedes exportar los datos filtrados para análisis externos</p>
        """)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: white;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        msg.exec()
    
    def limpiar_filtros(self):
        """Limpiar todos los filtros con feedback visual"""
        self.search_input.clear()
        self.meal_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.filtros_limpiados.emit()
        
        # Feedback visual
        self.clear_btn.setText("✅ Filtros Limpiados")
        QMessageBox.information(self, "🗑️ Filtros Limpiados", 
                               "Todos los filtros han sido restablecidos.")
        self.clear_btn.setText("🗑️ Limpiar Filtros")
    
    def obtener_datos_actuales(self):
        """Obtener los datos actuales de la tabla"""
        return self.datos_actuales
    
    def export_to_csv(self):
        """Exportar datos actuales a CSV con mejor UX"""
        if not self.datos_actuales:
            QMessageBox.warning(self, "⚠️ Sin datos", 
                               "No hay datos para exportar.\nIntenta ajustar los filtros.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "💾 Guardar CSV", "historial_consumo.csv", "CSV files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Escribir encabezados
                    writer.writerow(["Alimento", "Tipo", "Cantidad", "Calorías", "Fecha", "Hora", "Momento del Día"])
                    
                    # Escribir datos
                    for registro in self.datos_actuales:
                        writer.writerow([
                            registro[0], registro[1], registro[2], registro[3],
                            registro[4], registro[5], registro[6]
                        ])
                
                QMessageBox.information(self, "✅ Exportación Exitosa", 
                                       f"Datos exportados correctamente a:\n📁 {filename}\n\n"
                                       f"Total de registros: {len(self.datos_actuales)}")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error de Exportación", 
                                    f"Error al exportar:\n{str(e)}")