#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pantalla de bienvenida con banner
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPen

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2b2b2b, stop:0.5 #3c3c3c, stop:1 #2b2b2b);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título principal
        title = QLabel("BIENVENIDO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                margin-bottom: 20px;
                letter-spacing: 8px;
            }
        """)
        
        # Subtítulo
        subtitle = QLabel("APLICACIÓN DE CALORÍAS PRO\n60HZ")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 18, QFont.Weight.Normal))
        subtitle.setStyleSheet("""
            QLabel {
                color: #cccccc;
                background: transparent;
                letter-spacing: 3px;
                line-height: 1.5;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        # Agregar algunos iconos de frutas usando texto emoji
        self.add_fruit_decorations(layout)
        
    def add_fruit_decorations(self, layout):
        """Agregar decoraciones de frutas"""
        fruits_container = QWidget()
        fruits_container.setFixedHeight(200)
        fruits_container.setStyleSheet("background: transparent;")
        
        # Aquí podrías agregar más decoraciones o usar un widget personalizado
        # para dibujar las frutas como en tu imagen original
        
        layout.addWidget(fruits_container)
    
    def paintEvent(self, event):
        """Dibujar decoraciones adicionales"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen()
        pen.setColor(Qt.GlobalColor.white)
        pen.setWidth(2)
        painter.setPen(pen)
        