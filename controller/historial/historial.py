import sqlite3
import datetime
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, 
                             QFrame, QLabel, QPushButton, QTableView, QHeaderView,
                             QDateEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QAbstractTableModel, QDate
from .historialfacade import HistorialFacade

class HistorialTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Alimento", "Fecha", "Hora", "Cantidad", "Calorías"]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class HistorialView(QWidget):
    # Señales que la vista emite hacia el controlador
    aplicar_filtros_clicked = pyqtSignal()
    limpiar_filtros_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # --- Panel de Controles (Filtros) ---
        controles_frame = QFrame()
        controles_frame.setFixedHeight(60)
        controles_frame.setStyleSheet("background-color: #34495E; border-radius: 10px;")
        
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setContentsMargins(15, 5, 15, 5)

        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        
        self.btn_aplicar = QPushButton("Aplicar Filtro")
        self.btn_limpiar = QPushButton("Limpiar")
        
        controles_layout.addWidget(QLabel("Desde:"))
        controles_layout.addWidget(self.date_from)
        controles_layout.addWidget(QLabel("Hasta:"))
        controles_layout.addWidget(self.date_to)
        controles_layout.addStretch()
        controles_layout.addWidget(self.btn_aplicar)
        controles_layout.addWidget(self.btn_limpiar)

        # --- Tabla de Datos ---
        self.tabla = QTableView()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- Añadir widgets al layout principal de la vista ---
        layout.addWidget(controles_frame)
        layout.addWidget(self.tabla)
        
        # Conectar botones a las señales
        self.btn_aplicar.clicked.connect(self.aplicar_filtros_clicked.emit)
        self.btn_limpiar.clicked.connect(self.limpiar_filtros_clicked.emit)

        self.set_styles()

    def set_styles(self):
        date_style = """
            QDateEdit { 
                background-color: white; color: black; 
                border-radius: 5px; padding: 5px;
            }
        """
        btn_style = """
            QPushButton { 
                background-color: #2ECC71; color: #2C3E50; border: none;
                border-radius: 8px; padding: 8px 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27AE60; }
        """
        self.date_from.setStyleSheet(date_style)
        self.date_to.setStyleSheet(date_style)
        self.btn_aplicar.setStyleSheet(btn_style)
        self.btn_limpiar.setStyleSheet(btn_style.replace("#2ECC71", "#E74C3C").replace("#27AE60", "#C0392B"))
        self.tabla.setStyleSheet("""
            QTableView {
                background-color: #34495E; color: white;
                border: 1px solid #2C3E50; border-radius: 10px;
                gridline-color: #4A6572;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: #2ECC71;
                padding: 5px; border: none; font-weight: bold;
            }
            QTableView::item { padding: 5px; }
            QTableView::item:alternate { background-color: #3E576B; }
        """)

    def set_data_in_table(self, data):
        model = HistorialTableModel(data)
        self.tabla.setModel(model)


# ... (las clases HistorialTableModel y HistorialView se mantienen igual) ...

# --- Clase Principal (Controlador del Historial) ---
class Historial(QWidget):
    def __init__(self, panel_principal, color, usuario="test_user"):
        super().__init__()
        self.usuario = usuario
        # Se inicializa el Facade que habla con la API
        self.facade = HistorialFacade(self.usuario)
        self.init_ui()
        # Se carga la vista con datos iniciales de la API
        self.refrescar_vista()

    def init_ui(self):
        """Configura la interfaz principal del módulo Historial."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Historial de Consumo")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #FFFFFF; margin-bottom: 10px;")
        
        self.historial_view = HistorialView(self)
        
        main_layout.addWidget(titulo)
        main_layout.addWidget(self.historial_view)
        
        # Conectar las señales de la vista a los métodos del controlador
        self.historial_view.btn_aplicar.clicked.connect(self.aplicar_filtros)
        self.historial_view.btn_limpiar.clicked.connect(self.refrescar_vista)

    # --- MÉTODO ELIMINADO ---
    # _ejecutar_consulta ya no es necesario, porque no hablamos con la BD local.

    def refrescar_vista(self):
        """Recarga la vista con un rango de fechas por defecto (último año)."""
        # Resetea las fechas en la UI a un rango por defecto amplio
        self.historial_view.date_from.setDate(QDate.currentDate().addYears(-1))
        self.historial_view.date_to.setDate(QDate.currentDate())
        # Llama a aplicar_filtros para cargar los datos de ese rango por defecto
        self.aplicar_filtros()
        
    def aplicar_filtros(self):
        """Obtiene los datos de la API según el rango de fechas y actualiza la tabla."""
        fecha_desde = self.historial_view.date_from.date().toString("yyyy-MM-dd")
        fecha_hasta = self.historial_view.date_to.date().toString("yyyy-MM-dd")
        
        print(f"Pidiendo historial a la API entre {fecha_desde} y {fecha_hasta}...")
        
        # Usamos el facade para obtener datos de la API
        datos_api = self.facade.obtener_registros_por_rango(fecha_desde, fecha_hasta)
        
        if datos_api is None:
            QMessageBox.critical(self, "Error de API", "No se pudo obtener respuesta del servidor.")
            return

        # Convertimos los datos para que la tabla los entienda
        datos_para_tabla = self._formatear_datos_para_tabla(datos_api)
        self.historial_view.set_data_in_table(datos_para_tabla)

    def _formatear_datos_para_tabla(self, datos_api: list) -> list:
        """Convierte la lista de diccionarios de la API a una lista de tuplas para la tabla."""
        datos_formateados = []
        for consumo in datos_api:
            try:
                # La fecha de la API viene en yyyy-MM-dd, la formateamos a dd-MM-yyyy
                fecha_mostrada = datetime.datetime.strptime(consumo['fecha'], '%Y-%m-%d').strftime('%d-%m-%Y')
            except (ValueError, TypeError):
                fecha_mostrada = consumo.get('fecha', 'N/A')

            datos_formateados.append(
                (
                    consumo.get('nombre', 'N/A'),
                    fecha_mostrada,
                    consumo.get('hora', 'N/A'),
                    consumo.get('cantidad', 0),
                    round(consumo.get('total_cal', 0), 1)
                )
            )
        return datos_formateados
        
    def show_welcome_message(self):
        """Muestra un mensaje de bienvenida simple."""
        QMessageBox.information(
            self,
            "Historial de Consumo",
            "Aquí puedes ver y filtrar todos los alimentos que has registrado."
        )