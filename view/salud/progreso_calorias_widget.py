import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt

class ProgresoCaloriasWidget(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.progress_bar = None
        self.progress_label = None
        
        self.init_ui()
        self.refresh()

    def init_ui(self):
        """Inicializa la interfaz del widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Título del componente
        title_label = QLabel("Progreso de Calorías Diarias")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        main_layout.addWidget(title_label)

        # Barra de progreso para las calorías
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #555555;
                border: 1px solid #777;
                border-radius: 15px;
            }
            QProgressBar::chunk {
                background-color: #00FF7F; /* Verde Primavera */
                border-radius: 15px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Etiqueta para mostrar el texto del progreso (ej: 1500/2500 Kcal)
        self.progress_label = QLabel("0 / 0 Kcal")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        main_layout.addWidget(self.progress_label)
    
    def _fetch_data(self):
        """Obtiene los datos de calorías de la base de datos."""
        try:
            db_path = f"./users/{self.usuario}/alimentos.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Calorías consumidas hoy de la tabla `consumo_diario`
            today_date = datetime.now().strftime("%d-%m-%Y")
            cursor.execute("SELECT SUM(total_cal) FROM consumo_diario WHERE fecha = ?", (today_date,))
            result = cursor.fetchone()
            calorias_actuales = result[0] if result and result[0] is not None else 0
            
            # Meta de calorías del usuario de la tabla `datos`
            cursor.execute("SELECT meta_cal FROM datos WHERE nombre = ?", (self.usuario,))
            result = cursor.fetchone()
            meta_calorias = result[0] if result and result[0] is not None else 2000 # Valor por defecto

            conn.close()
            return calorias_actuales, meta_calorias
        except Exception as e:
            print(f"Error al obtener datos para el progreso de calorías: {e}")
            return 0, 2000 # Datos seguros en caso de error

    def refresh(self):
        """Actualiza la barra y el texto con datos frescos de la BD."""
        calorias_actuales, meta_calorias = self._fetch_data()
        
        # Actualizar la barra de progreso
        self.progress_bar.setMaximum(meta_calorias)
        self.progress_bar.setValue(min(int(calorias_actuales), meta_calorias))
        
        # Actualizar la etiqueta de texto
        self.progress_label.setText(f"{int(calorias_actuales)} / {meta_calorias} Kcal")