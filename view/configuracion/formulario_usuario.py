# En: view/configuracion/formulario_usuario.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QMessageBox


class UpdateUserForm(QDialog):
    def __init__(self, user_service, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Actualizar Información de Usuario")
        self.setFixedSize(400, 350)
        self.setModal(True) # Bloquea la ventana principal mientras está abierta
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                font-family: Arial;
            }
        """)

        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # --- Widgets del formulario ---
        # (Hecho de forma similar a la versión anterior)
        
        # Estatura
        estatura_layout = QHBoxLayout()
        estatura_label = QLabel("Estatura (cm)")
        estatura_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.estatura_input = QLineEdit()
        self.estatura_input.setStyleSheet("background-color: white; color: black; border-radius: 10px; padding: 5px;")
        estatura_layout.addWidget(estatura_label)
        estatura_layout.addWidget(self.estatura_input)
        
        # Objetivo
        objetivo_layout = QHBoxLayout()
        objetivo_label = QLabel("Objetivo (kcal)")
        objetivo_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.objetivo_input = QLineEdit()
        self.objetivo_input.setStyleSheet("background-color: white; color: black; border-radius: 10px; padding: 5px;")
        objetivo_layout.addWidget(objetivo_label)
        objetivo_layout.addWidget(self.objetivo_input)

        # Nivel Actividad
        actividad_layout = QHBoxLayout()
        actividad_label = QLabel("Nivel Actividad")
        actividad_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.actividad_combo = QComboBox()
        self.actividad_combo.addItems(["Sedentario", "Ligero", "Moderado", "Intenso"])
        self.actividad_combo.setStyleSheet("background-color: white; color: black; border-radius: 10px; padding: 5px;")
        actividad_layout.addWidget(actividad_label)
        actividad_layout.addWidget(self.actividad_combo)

        # --- Botones ---
        btn_actualizar = QPushButton("Actualizar datos")
        btn_actualizar.setStyleSheet("background-color: #2ECC71; color: #2C3E50; font-weight: bold; border-radius: 15px; padding: 10px;")
        
        btn_regresar = QPushButton("Regresar")
        btn_regresar.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; border-radius: 15px; padding: 10px;")

        # --- Conectar los botones a los slots de QDialog ---
        btn_actualizar.clicked.connect(self.accept) # Cierra el diálogo y retorna "Aceptado"
        btn_regresar.clicked.connect(self.reject)   # Cierra el diálogo y retorna "Rechazado"

        # --- Añadir todo al layout ---
        main_layout.addLayout(estatura_layout)
        main_layout.addLayout(objetivo_layout)
        main_layout.addLayout(actividad_layout)
        main_layout.addStretch()
        main_layout.addWidget(btn_actualizar)
        main_layout.addWidget(btn_regresar)

        self._load_data()

    def _load_data(self):
        """ Carga los datos actuales del usuario en los campos del formulario. """
        try:
            _, _, _, nivel_actividad, meta_cal, estatura = self.user_service.cargar_datos_usuario()
            self.estatura_input.setText(str(estatura))
            self.objetivo_input.setText(str(meta_cal))
            self.actividad_combo.setCurrentText(nivel_actividad)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del usuario: {e}")

    def get_data(self):
        """ Retorna los datos del formulario para ser guardados. """
        return {
            "estatura": self.estatura_input.text(),
            "meta_cal": self.objetivo_input.text(),
            "nivel_actividad": self.actividad_combo.currentText()
        }