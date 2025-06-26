from PyQt6.QtWidgets import (QLineEdit, QListWidget, QPushButton, 
                            QLabel, QFrame)
from PyQt6.QtGui import QFont

class UIManager:
    """Maneja la creación de elementos UI de manera consistente"""
    
    def __init__(self):
        self.default_font = QFont("Arial", 12)
        self.title_font = QFont("Arial", 16, QFont.Weight.Bold)
        
    def create_entry(self, parent, placeholder, x, y, width, height=35):
        """Crea un QLineEdit con placeholder y estilo consistente"""
        entry = QLineEdit(parent)
        entry.setPlaceholderText(placeholder)
        entry.move(x, y)
        entry.resize(width, height)
        entry.setFont(self.default_font)
        
        entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: #f9fff9;
            }
            QLineEdit:hover {
                border-color: #999999;
            }
        """)
        return entry
    
    def create_listbox(self, parent, x, y, width, height):
        """Crea un QListWidget con estilo consistente"""
        listbox = QListWidget(parent)
        listbox.move(x, y)
        listbox.resize(width, height)
        listbox.setFont(self.default_font)
        
        listbox.setStyleSheet("""
            QListWidget {
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #f0f8f0;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
        """)
        return listbox
    
    def create_button(self, parent, text, x, y, width, height, callback=None):
        """Crea un QPushButton con estilo consistente"""
        button = QPushButton(text, parent)
        button.move(x, y)
        button.resize(width, height)
        button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        if callback:
            button.clicked.connect(callback)
        
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                transform: translateY(1px);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        return button
    
    def create_label(self, parent, text, x, y, width=None, height=30, font_size=14):
        """Crea un QLabel con estilo consistente"""
        label = QLabel(text, parent)
        label.move(x, y)
        
        if width:
            label.resize(width, height)
        else:
            label.adjustSize()
        
        font = QFont("Arial", font_size)
        label.setFont(font)
        
        label.setStyleSheet(f"""
            QLabel {{
                color: #333333;
                padding: 2px;
            }}
        """)
        
        return label
    
    def create_frame(self, parent, x, y, width, height, color="#f0f0f0", border_radius=10):
        """Crea un QFrame como contenedor con estilo"""
        frame = QFrame(parent)
        frame.move(x, y)
        frame.resize(width, height)
        
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: {border_radius}px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }}
        """)
        return frame
    
    def create_title_label(self, parent, text, x, y, width=None, height=40):
        """Crea un label para títulos con estilo especial"""
        label = self.create_label(parent, text, x, y, width, height, 18)
        label.setFont(self.title_font)
        label.setStyleSheet("""
            QLabel {
                color: #2E86AB;
                font-weight: bold;
                padding: 5px;
            }
        """)
        return label
    
    def create_info_frame(self, parent, x, y, width, height, title, content=""):
        """Crea un frame informativo con título y contenido"""
        # Frame principal
        frame = self.create_frame(parent, x, y, width, height, "#E3F2FD")
        
        # Título
        title_label = self.create_label(parent, title, x + 10, y + 5, width - 20, 25, 14)
        title_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        
        # Contenido
        content_label = self.create_label(parent, content, x + 10, y + 30, width - 20, height - 35, 12)
        content_label.setStyleSheet("""
            QLabel {
                color: #424242;
                background-color: transparent;
                padding: 5px;
            }
        """)
        content_label.setWordWrap(True)
        
        return frame, title_label, content_label
    
    def create_warning_button(self, parent, text, x, y, width, height, callback=None):
        """Crea un botón de advertencia con estilo especial"""
        button = self.create_button(parent, text, x, y, width, height, callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                border: none;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        return button
    
    def create_success_button(self, parent, text, x, y, width, height, callback=None):
        """Crea un botón de éxito con estilo especial"""
        button = self.create_button(parent, text, x, y, width, height, callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #45a049;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
        """)
        return button
    
    def apply_modern_style(self, widget):
        """Aplica un estilo moderno a cualquier widget"""
        widget.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QWidget {
                background-color: #fafafa;
            }
            QFrame {
                border-radius: 8px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QLineEdit {
                border-radius: 6px;
                padding: 8px 12px;
                border: 1px solid #ddd;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
        """)