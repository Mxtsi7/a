import os
import sqlite3

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath


class ProfileWidget(QWidget):
    """Widget para la foto de perfil que emite una señal cuando cambia."""
    picture_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        self.profile_container = QFrame()
        self.profile_container.setFixedSize(80, 80)
        self.profile_container.setStyleSheet("background-color: transparent;")

        profile_layout = QVBoxLayout(self.profile_container)
        profile_layout.setContentsMargins(0, 0, 0, 0)

        self.profile_image = QLabel()
        self.profile_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_image.setFixedSize(80, 80)
        self.profile_image.setStyleSheet("""
            QLabel {
                border: 3px solid #4CAF50;
                border-radius: 40px;
                background-color: #5a5a5a;
            }
        """)
        self.profile_image.setScaledContents(True)
        profile_layout.addWidget(self.profile_image)

        self.add_photo_btn = QPushButton("+")
        self.add_photo_btn.setFixedSize(24, 24)
        self.add_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: white; border: 2px solid #2b2b2b;
                border-radius: 12px; font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background-color: #27AE60; }
        """)
        self.add_photo_btn.clicked.connect(self.select_photo)
        self.add_photo_btn.setParent(self.profile_container)
        self.add_photo_btn.move(56, 56)

        self.username_label = QLabel("Usuario")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 5px;")

        layout.addWidget(self.profile_container)
        layout.addWidget(self.username_label)

    def select_photo(self):
        """Abre un diálogo para seleccionar una foto y emite una señal."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar foto de perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg)",
            options=QFileDialog.Option.DontUseNativeDialog
        )

        if file_path:
            self.set_picture(file_path)
            self.picture_changed.emit(file_path)

    def set_picture(self, image_path):
        """Carga y muestra una imagen en el label circular con recorte real."""
        if image_path and os.path.exists(image_path):
            original = QPixmap(image_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            masked = QPixmap(80, 80)
            masked.fill(Qt.GlobalColor.transparent)

            painter = QPainter(masked)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, 80, 80)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, original)
            painter.end()

            self.profile_image.setPixmap(masked)
        else:
            self.profile_image.setPixmap(QPixmap())
            self.profile_image.setText("👤")
            self.profile_image.setStyleSheet(self.profile_image.styleSheet() + "font-size: 40px; color: #ccc;")


class NavigationButton(QPushButton):
    """Botón de navegación personalizado."""
    def __init__(self, text, icon_text=""):
        super().__init__()
        self.setText(f"{icon_text}  {text}")
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #cccccc; border: none;
                text-align: left; padding-left: 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #4a4a4a; color: white; }
            QPushButton:pressed { background-color: #5a5a5a; }
        """)


class Sidebar(QWidget):
    """Barra lateral principal."""
    section_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.usuario = None
        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(0)

        self.profile_widget = ProfileWidget()
        self.profile_widget.picture_changed.connect(self._save_profile_pic_to_db)
        layout.addWidget(self.profile_widget)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #4a4a4a; }")
        layout.addWidget(separator)
        layout.addSpacing(20)

        self.create_navigation_buttons(layout)
        layout.addStretch()

    def create_navigation_buttons(self, layout):
        buttons_data = [
            ("Registrar Alimento", "📝", "registrar"),
            ("Agregar Alimento", "➕", "agregar"),
            ("Gráfico", "📊", "grafico"),
            ("Historial", "🕐", "historial"),
            ("Settings", "⚙️", "settings"),
            ("Salud", "🛡️", "salud"),
            ("Menu", "📋", "menu")
        ]

        for text, icon, section_id in buttons_data:
            btn = NavigationButton(text, icon)
            btn.clicked.connect(lambda checked, s=section_id: self.section_changed.emit(s))
            layout.addWidget(btn)
            layout.addSpacing(5)

    def set_usuario(self, usuario: str):
        self.usuario = usuario
        self.profile_widget.username_label.setText(self.usuario)
        self._load_profile_pic_from_db()

    def _load_profile_pic_from_db(self):
        if not self.usuario:
            return
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            cursor.execute("SELECT profile_pic_path FROM datos WHERE nombre = ?", (self.usuario,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                self.profile_widget.set_picture(result[0])
            else:
                self.profile_widget.set_picture(None)
        except Exception as e:
            print(f"Error al cargar la ruta de la imagen: {e}")
            self.profile_widget.set_picture(None)

    def _save_profile_pic_to_db(self, path: str):
        if not self.usuario:
            return
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE datos SET profile_pic_path = ? WHERE nombre = ?", (path, self.usuario))
            conn.commit()
            conn.close()
            print(f"Ruta de imagen guardada para {self.usuario}: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Guardado", "No se pudo guardar la ruta de la imagen en la base de datos.")
