import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QDateEdit, QComboBox,
                             QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont

class Agregar_Recordatorio(QDialog):
    # Señal para notificar cuando se agrega un recordatorio
    recordatorio_agregado = pyqtSignal()
    
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.configurar_ventana()
        self.crear_widgets()
        self.setup_styles()

    def configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.setFixedSize(400, 350)
        self.setWindowTitle("Agregar Recordatorio")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

    def crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título principal
        self.label_titulo = QLabel("Agregue un recordatorio")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(self.label_titulo)

        # Título del recordatorio
        self.label_titulorecordatorio = QLabel("Título del recordatorio:")
        main_layout.addWidget(self.label_titulorecordatorio)
        
        self.entry_titulorecordatorio = QLineEdit()
        self.entry_titulorecordatorio.setPlaceholderText("Ingrese el título del recordatorio")
        main_layout.addWidget(self.entry_titulorecordatorio)

        # Fecha
        self.datetime_label = QLabel("Fecha:")
        main_layout.addWidget(self.datetime_label)

        self.date_entry = QDateEdit()
        self.date_entry.setDate(QDate.currentDate())
        self.date_entry.setCalendarPopup(True)
        self.date_entry.setDisplayFormat("yyyy-MM-dd")
        main_layout.addWidget(self.date_entry)

        # Hora
        self.hora_label = QLabel("Hora:")
        main_layout.addWidget(self.hora_label)

        # Frame para los combobox de hora
        hora_frame = QFrame()
        hora_layout = QHBoxLayout(hora_frame)
        hora_layout.setContentsMargins(0, 0, 0, 0)

        # ComboBox de horas
        self.combo_horas = QComboBox()
        horas = [f"{h:02d}" for h in range(24)]
        self.combo_horas.addItems(horas)
        self.combo_horas.setCurrentText("12")
        self.combo_horas.setFixedWidth(60)
        hora_layout.addWidget(self.combo_horas)

        # Separador
        separator = QLabel(":")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        hora_layout.addWidget(separator)

        # ComboBox de minutos
        self.combo_minutos = QComboBox()
        minutos = [f"{m:02d}" for m in range(60)]
        self.combo_minutos.addItems(minutos)
        self.combo_minutos.setCurrentText("00")
        self.combo_minutos.setFixedWidth(60)
        hora_layout.addWidget(self.combo_minutos)

        # Espaciador para centrar los combobox
        hora_layout.addStretch()
        
        main_layout.addWidget(hora_frame)

        # Espaciador
        main_layout.addStretch()

        # Botones
        button_layout = QHBoxLayout()
        
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        button_layout.addWidget(self.boton_cancelar)

        self.boton_agregar = QPushButton("Agregar")
        self.boton_agregar.clicked.connect(self.guardar_recordatorio)
        self.boton_agregar.setDefault(True)  # Botón por defecto al presionar Enter
        button_layout.addWidget(self.boton_agregar)

        main_layout.addLayout(button_layout)

    def setup_styles(self):
        """Configura los estilos de los widgets"""
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #34495E;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
            QDateEdit {
                background-color: #34495E;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: white;
            }
            QDateEdit:focus {
                border-color: #3498DB;
            }
            QComboBox {
                background-color: #34495E;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                color: white;
            }
            QComboBox:focus {
                border-color: #3498DB;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)

        # Estilo del título principal
        self.label_titulo.setStyleSheet("""
            QLabel {
                color: #3498DB;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        # Estilo del botón agregar
        self.boton_agregar.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        # Estilo del botón cancelar
        self.boton_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
            QPushButton:pressed {
                background-color: #6C7B7D;
            }
        """)

    def guardar_recordatorio(self):
        """Guarda el recordatorio en la base de datos"""
        # Validar que se haya ingresado un título
        titulo = self.entry_titulorecordatorio.text().strip()
        if not titulo:
            self.mostrar_mensaje("Error", "Por favor ingrese un título para el recordatorio.", 
                                QMessageBox.Icon.Warning)
            return

        # Obtener los datos del formulario
        fecha = self.date_entry.date().toString("yyyy-MM-dd")
        hora = self.combo_horas.currentText()
        minutos = self.combo_minutos.currentText()
        hora_completa = f"{hora}:{minutos}"

        try:
            # Crear directorio del usuario si no existe
            import os
            user_dir = f"./users/{self.usuario}"
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)

            # Conectar a la base de datos
            with sqlite3.connect(f"./users/{self.usuario}/alimentos.db") as conn:
                cursor = conn.cursor()
                
                # Crear tabla de recordatorios si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recordatorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        fecha TEXT NOT NULL,
                        hora TEXT NOT NULL,
                        usuario TEXT NOT NULL,
                        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insertar el recordatorio
                cursor.execute("""
                    INSERT INTO recordatorios (titulo, fecha, hora, usuario) 
                    VALUES (?, ?, ?, ?)
                """, (titulo, fecha, hora_completa, self.usuario))
                
                conn.commit()
                
                # Mostrar mensaje de éxito
                self.mostrar_mensaje("Éxito", "Recordatorio agregado correctamente.", 
                                    QMessageBox.Icon.Information)
                
                # Emitir señal de que se agregó el recordatorio
                self.recordatorio_agregado.emit()
                
                # Cerrar el diálogo
                self.accept()
                
        except sqlite3.Error as e:
            self.mostrar_mensaje("Error", f"No se pudo agregar el recordatorio: {str(e)}", 
                                QMessageBox.Icon.Critical)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error inesperado: {str(e)}", 
                                QMessageBox.Icon.Critical)

    def mostrar_mensaje(self, titulo, mensaje, icono):
        """Muestra un mensaje al usuario"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(icono)
        msg_box.exec()

    def keyPressEvent(self, event):
        """Maneja los eventos de teclado"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not event.modifiers():  # Solo Enter, no Ctrl+Enter
                self.guardar_recordatorio()
        else:
            super().keyPressEvent(event)